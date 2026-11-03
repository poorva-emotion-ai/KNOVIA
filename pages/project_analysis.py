
import streamlit as st

import db_operations
from ai_engine.rag_pipeline import generate_answer


st.title("🤖 AI Project Analysis")
st.caption("Ask questions and explore your project's knowledge using Gemini RAG.")

st.divider()


# ==========================================
# LOAD PROJECTS
# ==========================================

try:
    projects = db_operations.get_projects_for_dashboard()

except Exception as error:
    st.error(f"Unable to load projects: {error}")
    st.stop()


if not projects:
    st.info("No projects available. Please create a project first.")
    st.stop()


project_options = {
    f"{project['name']} (ID: {project['id']})": project
    for project in projects
}

selected_project_label = st.selectbox(
    "Select Project",
    list(project_options.keys())
)

selected_project = project_options[selected_project_label]
project_id = selected_project["id"]


st.divider()


# ==========================================
# LOAD PROJECT DOCUMENTS
# ==========================================

st.subheader("📄 Select Project Documents")

try:
    documents = db_operations.get_project_documents(project_id)

except Exception as error:
    st.error(f"Unable to load project documents: {error}")
    st.stop()


if not documents:
    st.warning("Upload project documents before starting AI analysis.")
    st.stop()


document_options = {
    f"{document[2]} (ID: {document[0]})": document[0]
    for document in documents
}

selected_document_labels = st.multiselect(
    "Choose documents for analysis",
    options=list(document_options.keys()),
    default=list(document_options.keys())
)

selected_document_ids = [
    document_options[label]
    for label in selected_document_labels
]


st.divider()


# ==========================================
# ASK GEMINI
# ==========================================

st.subheader("💬 Ask KNOVIA")

st.write(
    "Ask questions about your project documents. "
    "KNOVIA retrieves relevant information and generates an AI answer."
)

with st.form("ai_analysis_form"):

    question = st.text_area(
        "Your Question",
        placeholder="Example: What are the main objectives of this project?",
        height=120
    )

    submitted = st.form_submit_button(
        "🔍 Analyse Project",
        use_container_width=True
    )


if submitted:

    if not question.strip():

        st.warning("Please enter a question.")

    elif not selected_document_ids:

        st.warning("Please select at least one document.")

    else:

        try:

            with st.spinner("KNOVIA is analysing your documents..."):

                answer = generate_answer(
                    question=question.strip(),
                    project_id=project_id,
                    document_ids=selected_document_ids
                )

            st.session_state["analysis_result"] = {
                "project_id": project_id,
                "question": question.strip(),
                "answer": answer
            }

        except Exception as error:

            st.error(f"AI analysis failed: {error}")


# ==========================================
# DISPLAY GEMINI RESPONSE
# ==========================================

result = st.session_state.get("analysis_result")

if result and result["project_id"] == project_id:

    st.divider()

    st.subheader("🧠 KNOVIA AI Response")

    st.markdown(f"**Question:** {result['question']}")

    st.markdown(result["answer"])

    st.caption(
        "AI-generated answer based on the selected project documents. "
        "Verify important findings against the original sources."
    )
