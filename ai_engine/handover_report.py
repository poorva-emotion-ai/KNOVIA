
from ai_engine.rag_pipeline import analyze_member_exit
from embedding_store import list_documents
from ai_engine.takeover_recommender import recommend_takeover

from db_operations import (
    get_project_members,
    get_project_documents,
    get_tasks_for_takeover,
    get_members_for_takeover,
    add_takeover_recommendation,
    add_handover_report
)


def generate_handover_report(
    project_id,
    departing_member_id,
    document_ids=None
):
    """
    Generate and save a project handover report.

    Uses actual SQLite project data and indexed ChromaDB documents.
    All saved reports remain Pending until leader approval.
    """

    project_id = int(project_id)
    departing_member_id = int(departing_member_id)

    # -------------------------------------------------
    # 1. Validate project member
    # -------------------------------------------------

    members = get_project_members(project_id)

    departing_record = next(
        (
            member for member in members
            if int(member[0]) == departing_member_id
        ),
        None
    )

    if departing_record is None:
        raise ValueError(
            "Departing member does not belong to this project."
        )

    # Database member columns:
    # id, project_id, name, role, skills, member_name, email,
    # current_workload

    departing_name = (
        departing_record[5] or departing_record[2]
    )

    # -------------------------------------------------
    # 2. Select actual project documents indexed in ChromaDB
    # -------------------------------------------------

    project_documents = get_project_documents(project_id)

    database_document_ids = {
        int(document[0])
        for document in project_documents
    }

    indexed_documents = list_documents(project_id)

    indexed_document_ids = {
        int(document["document_id"])
        for document in indexed_documents
    }

    available_document_ids = (
        database_document_ids & indexed_document_ids
    )

    if document_ids is None:
        selected_document_ids = sorted(
            available_document_ids
        )
    else:
        selected_document_ids = sorted({
            int(document_id)
            for document_id in document_ids
            if int(document_id) in available_document_ids
        })

    # -------------------------------------------------
    # 3. Generate AI member exit analysis
    # -------------------------------------------------

    if selected_document_ids:

        exit_analysis = analyze_member_exit(
            project_id=project_id,
            document_ids=selected_document_ids,
            departing_member=departing_name
        )

    else:
        exit_analysis = (
            "No indexed project documents were available "
            "for AI exit analysis. Document knowledge "
            "must be verified by the project leader."
        )

    # -------------------------------------------------
    # 4. Retrieve unfinished tasks from SQLite
    # -------------------------------------------------

    unfinished_tasks = get_tasks_for_takeover(
        project_id,
        departing_member_id
    )

    # -------------------------------------------------
    # 5. Retrieve remaining team members
    # -------------------------------------------------

    team_members = get_members_for_takeover(
        project_id,
        departing_member_id
    )

    # -------------------------------------------------
    # 6. Generate AI takeover recommendations
    # -------------------------------------------------

    recommendations = recommend_takeover(
        unfinished_responsibilities=unfinished_tasks,
        team_members=team_members,
        departing_member=departing_name
    )

    # -------------------------------------------------
    # 7. Save recommendations using real database IDs
    # -------------------------------------------------

    saved_recommendation_ids = []

    for recommendation in recommendations:

        task_id = recommendation.get("task_id")

        candidate = recommendation["candidate"]

        recommended_member_id = candidate.get("member_id")

        if task_id is None or recommended_member_id is None:
            continue

        existing_work = recommendation["existing_work_details"]

        verification_notes = recommendation["verification_needed"]

        reason = (
            f"Skill match: "
            f"{candidate['skill_match_percentage']}%. "
            f"Match level: {candidate['skill_match_level']}. "
            f"Matched skills: "
            f"{', '.join(candidate['matched_skills'])}. "
            f"Current workload: "
            f"{existing_work['current_workload']}. "
            f"Verification required: "
            f"{'; '.join(verification_notes) if verification_notes else 'None'}."
        )

        recommendation_id = add_takeover_recommendation(
            project_id=project_id,
            task_id=task_id,
            departing_member_id=departing_member_id,
            recommended_member_id=recommended_member_id,
            reason=reason
        )

        saved_recommendation_ids.append(recommendation_id)

    # -------------------------------------------------
    # 8. Prepare incoming member guide
    # -------------------------------------------------

    guide_sections = [
        "KNOVIA - INCOMING MEMBER GUIDE",
        "=" * 45,
        f"Project ID: {project_id}",
        f"Departing Member: {departing_name}",
        "",
        "1. PROJECT KNOWLEDGE",
        exit_analysis,
        "",
        "2. UNFINISHED RESPONSIBILITIES"
    ]

    if unfinished_tasks:
        for task in unfinished_tasks:
            guide_sections.append(
                f"- Task: {task['task']}"
            )
            guide_sections.append(
                f"  Status: {task['status']}"
            )
            guide_sections.append(
                f"  Description: {task['description'] or 'Not specified'}"
            )
            guide_sections.append(
                "  Required skills: "
                + (
                    ", ".join(task["required_skills"])
                    if task["required_skills"]
                    else "Not specified"
                )
            )
    else:
        guide_sections.append(
            "No unfinished tasks are currently recorded "
            "for this member in the database."
        )

    guide_sections.extend([
        "",
        "3. TAKEOVER RECOMMENDATIONS"
    ])

    if recommendations:
        for item in recommendations:
            candidate = item["candidate"]

            guide_sections.append(
                f"- Task: {item['task']}"
            )
            guide_sections.append(
                f"  Suggested member: {candidate['name']}"
            )
            guide_sections.append(
                f"  Skill match: "
                f"{candidate['skill_match_percentage']}%"
            )
            guide_sections.append(
                f"  Match level: {candidate['skill_match_level']}"
            )
            guide_sections.append(
                "  Decision: Awaiting human approval"
            )
    else:
        guide_sections.append(
            "No suitable skill matches were found. "
            "The project leader must review available team members "
            "and assign responsibilities manually."
        )

    guide_sections.extend([
        "",
        "4. VERIFICATION CHECKLIST",
        "- Verify unfinished tasks and their current status.",
        "- Confirm the incoming member has sufficient availability.",
        "- Verify technical documentation and dependencies.",
        "- Review all AI-generated recommendations.",
        "- Obtain project leader approval before assigning work.",
        "",
        "IMPORTANT: This guide is generated from available "
        "project records and indexed documents. Missing "
        "information requires human verification.",
        "",
        "Approval Status: Pending"
    ])

    incoming_member_guide = "\n".join(guide_sections)

    # -------------------------------------------------
    # 9. Prepare complete handover report
    # -------------------------------------------------

    report_sections = [
        "KNOVIA - PROJECT HANDOVER REPORT",
        "=" * 45,
        f"Project ID: {project_id}",
        f"Departing Member: {departing_name}",
        "",
        "MEMBER EXIT ANALYSIS",
        "-" * 30,
        str(exit_analysis),
        "",
        "UNFINISHED RESPONSIBILITIES",
        "-" * 30
    ]

    if unfinished_tasks:
        for task in unfinished_tasks:
            report_sections.append(
                f"Task ID: {task['task_id']}"
            )
            report_sections.append(
                f"Task: {task['task']}"
            )
            report_sections.append(
                f"Status: {task['status']}"
            )
            report_sections.append("")
    else:
        report_sections.append(
            "No unfinished tasks recorded."
        )

    report_sections.extend([
        "TAKEOVER RECOMMENDATIONS",
        "-" * 30
    ])

    if recommendations:
        for item in recommendations:
            candidate = item["candidate"]

            report_sections.append(
                f"Task: {item['task']}"
            )
            report_sections.append(
                f"Suggested member: {candidate['name']}"
            )
            report_sections.append(
                f"Skill match: "
                f"{candidate['skill_match_percentage']}%"
            )
            report_sections.append(
                f"Match level: {candidate['skill_match_level']}"
            )
            report_sections.append(
                "Decision: Awaiting human approval"
            )
            report_sections.append("")
    else:
        report_sections.append(
            "No suitable skill matches found."
        )

    report_sections.extend([
        "DATABASE STATUS",
        "-" * 30,
        f"Saved recommendations: {len(saved_recommendation_ids)}",
        "Approval Status: Pending"
    ])

    report_content = "\n".join(report_sections)

    # -------------------------------------------------
    # 10. Save handover report in SQLite
    # -------------------------------------------------

    report_id = add_handover_report(
        project_id=project_id,
        departing_member_id=departing_member_id,
        report_content=report_content,
        incoming_member_guide=incoming_member_guide
    )

    # -------------------------------------------------
    # 11. Return results to the frontend
    # -------------------------------------------------

    return {
        "report_id": report_id,
        "project_id": project_id,
        "departing_member_id": departing_member_id,
        "departing_member": departing_name,
        "member_exit_analysis": exit_analysis,
        "unfinished_responsibilities": unfinished_tasks,
        "takeover_recommendations": recommendations,
        "saved_recommendation_ids": saved_recommendation_ids,
        "incoming_member_guide": incoming_member_guide,
        "report_content": report_content,
        "approval_status": "Pending"
    }
