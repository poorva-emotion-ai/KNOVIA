
def recommend_takeover(unfinished_responsibilities, team_members, departing_member):

    recommendations = []

    for responsibility in unfinished_responsibilities:

        task_name = responsibility["task"]

        required_skills = {
            skill.lower()
            for skill in responsibility.get("required_skills", [])
        }

        for member in team_members:

            # Do not recommend the departing member
            if member["name"].lower() == departing_member.lower():
                continue

            member_skills = {
                skill.lower()
                for skill in member.get("skills", [])
            }

            # Find matching skills
            matched_skills = required_skills.intersection(member_skills)

            if not matched_skills:
                continue

            # Calculate skill coverage
            skill_match_percentage = (
                len(matched_skills) / len(required_skills) * 100
                if required_skills else 0
            )

            # Classify candidate based on skill coverage
            if skill_match_percentage >= 80:
                skill_match_level = "Strong Match"

            elif skill_match_percentage >= 50:
                skill_match_level = "Partial Match"

            else:
                skill_match_level = "Limited Match"

            # Get workload and existing responsibilities
            workload = member.get("current_workload", "unknown")

            current_responsibilities = member.get(
                "current_responsibilities", []
            )

            verification_needed = []

            # Unknown workload must be verified
            if not workload or workload.lower() == "unknown":

                verification_needed.append(
                    "Current workload needs verification."
                )

            elif workload.lower() == "high":

                verification_needed.append(
                    "Member has a high workload. Check availability."
                )

            # Store structured recommendation
            recommendations.append({

                "task": task_name,
                "task_id": responsibility.get("task_id"),

                "candidate": {
                    "member_id": member.get("member_id"),
                    "name": member["name"],
                    "matched_skills": sorted(matched_skills),
                    "skill_match_percentage": round(
                        skill_match_percentage, 2
                    ),
                    "skill_match_level": skill_match_level
                },

                "existing_work_details": {
                    "current_workload": workload,
                    "current_responsibilities": current_responsibilities
                },

                "verification_needed": verification_needed,

                "decision": "Awaiting human approval"

            })

    return recommendations


# Display the recommendations in a readable format
def display_recommendations(recommendations):

    print("\n" + "=" * 55)
    print("       KNOVIA - TAKEOVER RECOMMENDATION REPORT")
    print("=" * 55)

    if not recommendations:
        print("\nNo suitable skill matches found.")
        return

    for index, item in enumerate(recommendations, start=1):

        candidate = item["candidate"]
        work = item["existing_work_details"]

        print(f"\nCandidate {index}")
        print("-" * 55)

        print(f"Unfinished Task: {item['task']}")
        print(f"Member Name: {candidate['name']}")

        print("\nSKILL COMPATIBILITY")
        print(f"Matched Skills: {', '.join(candidate['matched_skills'])}")
        print(f"Skill Match: {candidate['skill_match_percentage']}%")
        print(f"Match Level: {candidate['skill_match_level']}")

        print("\nEXISTING WORK DETAILS")
        print(f"Current Workload: {work['current_workload']}")

        responsibilities = work["current_responsibilities"]

        if responsibilities:
            for responsibility in responsibilities:
                print(f"- {responsibility}")
        else:
            print("No existing responsibilities documented.")

        print("\nVERIFICATION REQUIRED")

        if item["verification_needed"]:
            for note in item["verification_needed"]:
                print(f"- {note}")
        else:
            print("No additional verification flags.")

        print(f"\nDecision: {item['decision']}")

    print("\n" + "=" * 55)
    print("Final assignment requires human approval.")
    print("=" * 55)


# Main execution
if __name__ == "__main__":

    # Temporary test responsibility
    unfinished_responsibilities = [
        {
            "task": "Backend API Development",
            "required_skills": [
                "Python",
                "Backend Development",
                "REST API Development"
            ]
        }
    ]

    # Temporary test team data
    team_members = [
        {
            "name": "Aarav",
            "skills": ["Python", "Backend Development"],
            "current_workload": "high",
            "current_responsibilities": [
                "Backend API Development"
            ]
        },
        {
            "name": "Meera",
            "skills": ["Python", "SQL", "Database Design"],
            "current_workload": "unknown",
            "current_responsibilities": [
                "Database Integration"
            ]
        },
        {
            "name": "Riya",
            "skills": ["HTML", "CSS", "JavaScript"],
            "current_workload": "low",
            "current_responsibilities": [
                "Frontend Development"
            ]
        },
        {
            "name": "Kabir",
            "skills": [
                "Python",
                "Backend Development",
                "REST API Development"
            ],
            "current_workload": "low",
            "current_responsibilities": [
                "Frontend API Integration",
                "Bug Fixing"
            ]
        }
    ]

    result = recommend_takeover(
        unfinished_responsibilities,
        team_members,
        departing_member="Aarav"
    )

    display_recommendations(result)
