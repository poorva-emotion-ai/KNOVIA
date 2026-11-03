import streamlit as st
import tempfile


from pathlib import Path

import db_operations
from ai_engine.rag_pipeline import process_and_store_document


st.title("Project Knowledge")
st.caption("Upload documents and record important project updates.")

# ==========================================
# LOAD PROJECTS FROM SQLITE
# ==========================================

try:
    projects = db_operations.get_projects_for_dashboard()

except Exception as error:
    st.error(f"Unable to load projects: {error}")
    st.stop()


if not projects:
    st.warning("Please create a project first.")
    st.stop()


# Handle projects with duplicate names
project_options = {
    f"{project['name']} (ID: {project['id']})": project
    for project in projects
}


selected_label = st.selectbox(
    "Select Project",
    list(project_options.keys())
)

selected_project = project_options[selected_label]

project_id = selected_project["id"]


st.divider()


# ==========================================
# DOCUMENTS AND MANUAL UPDATES
# ==========================================

tab1, tab2 = st.tabs([
    "📄 Upload Documents",
    "✏️ Manual Updates"
])


# ==========================================
# TAB 1: DOCUMENT UPLOAD
# ==========================================

# ==========================================
# TAB 1: DOCUMENT UPLOAD
# ==========================================

with tab1:

    st.subheader("Upload Project Documents")

    st.write(
        "Upload PDF or DOCX documents to build your project's knowledge base."
    )

    uploaded_files = st.file_uploader(
        "Choose your files",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if st.button(
        "Save Documents",
        use_container_width=True
    ):

        if not uploaded_files:

            st.warning("Please select at least one document.")

        else:

            for uploaded_file in uploaded_files:

                try:

                    # Preserve the original uploaded filename
                    with tempfile.TemporaryDirectory() as temp_dir:

                        temp_path = (
                            Path(temp_dir) /
                            Path(uploaded_file.name).name
                        )

                        temp_path.write_bytes(
                            uploaded_file.getvalue()
                        )

                        # Process and save document in SQLite
                        result = process_and_store_document(
                            project_id=project_id,
                            file_path=temp_path
                            )

                        st.success(
                            f"Successfully uploaded: {result['file_name']}"
                        )

                        st.caption(
                            f"Document ID: {result['document_id']}"
                        )

                except Exception as error:

                    st.error(
                        f"Could not upload {uploaded_file.name}: {error}"
                    )



# ==========================================
# TAB 2: MANUAL PROJECT UPDATES
# ==========================================

with tab2:

    st.subheader("Add Project Update")

    st.write(
        "Record progress, decisions and important project information."
    )

    update_type = st.selectbox(
        "Update Category",
        [
            "Progress Update",
            "Important Decision",
            "Technical Information",
            "Issue / Challenge",
            "Other"
        ]
    )

    update_title = st.text_input(
        "Update Title",
        placeholder="Enter a short title"
    )

    update_description = st.text_area(
        "Update Details",
        placeholder="Describe the update in detail...",
        height=150
    )

    if st.button(
        "Save Update",
        use_container_width=True
    ):

        if not update_title.strip() or not update_description.strip():

            st.error("Please fill in the title and details.")

        else:

            try:

                if update_type == "Important Decision":

                    db_operations.add_decision(
                        project_id,
                        update_title.strip(),
                        update_description.strip()
                    )

                else:

                    update_text = (
                        f"[{update_type}]\n"
                        f"Title: {update_title.strip()}\n"
                        f"Details: {update_description.strip()}"
                    )

                    db_operations.add_update(
                        project_id,
                        None,
                        update_text
                    )

                st.success("Project information saved successfully!")

            except Exception as error:

                st.error(f"Could not save update: {error}")


# ==========================================
# SAVED PROJECT INFORMATION
# ==========================================

st.divider()

st.header("Saved Project Information")

col1, col2 = st.columns(2)


# ==========================================
# DISPLAY SAVED DOCUMENTS
# ==========================================

with col1:

    st.subheader("📄 Uploaded Documents")

    try:

        documents = db_operations.get_project_documents(
            project_id
        )

        if documents:

            for document in documents:

                with st.container(border=True):

                    st.write(f"📄 {document[2]}")

                    st.caption(
                        f"Uploaded: {document[4]}"
                    )

                    st.caption(
                        f"Document ID: {document[0]}"
                    )

        else:

            st.info("No documents uploaded yet.")

    except Exception as error:

        st.error(f"Unable to retrieve documents: {error}")


# ==========================================
# DISPLAY SAVED UPDATES
# ==========================================

with col2:

    st.subheader("📝 Project Updates")

    try:

        updates = db_operations.get_project_updates(
            project_id
        )

        if updates:

            for update in reversed(updates):

                with st.container(border=True):

                    st.write(update[3])

                    st.caption(
                        f"Date: {update[4]}"
                    )

        else:

            st.info("No project updates recorded yet.")

    except Exception as error:

        st.error(f"Unable to retrieve updates: {error}")