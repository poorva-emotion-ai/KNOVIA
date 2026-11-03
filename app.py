
import streamlit as st
from database import create_database
from update_database import update_database

# Initialise database before loading pages
create_database()
update_database()

st.set_page_config(
    page_title="KNOVIA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# KNOVIA - Royal Blue & Pearl Theme
st.markdown("""
<style>

/* Main application background */
.stApp {
    background-color: #F8FAFC;
    color: #23395B;
}

/* Main content spacing */
.block-container {
    padding: 2rem 3rem;
    max-width: 1500px;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #23395B;
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: #F8FAFC;
}

/* Sidebar header layout */
[data-testid="stSidebarHeader"] {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 12px;
    position: relative;
}

/* KNOVIA logo and name on the LEFT */
[data-testid="stSidebarHeader"]::before {
    content: "KNOVIA";
    display: block;
    order: 0;
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 1px;
    white-space: nowrap;

    padding-left: 34px;
    min-height: 28px;
    line-height: 28px;

    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32' fill='none' stroke='%238EA8C3' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M16 9V15M16 15H7V21M16 15H25V21'/%3E%3Ccircle cx='16' cy='6' r='3' fill='%238EA8C3'/%3E%3Ccircle cx='7' cy='24' r='3' fill='%238EA8C3'/%3E%3Ccircle cx='25' cy='24' r='3' fill='%238EA8C3'/%3E%3C/svg%3E");

    background-repeat: no-repeat;
    background-position: left center;
    background-size: 28px 28px;
}

/* Collapse arrow on the RIGHT */
[data-testid="stSidebarHeader"] [data-testid="stSidebarCollapseButton"] {
    order: 1;
    margin-left: auto;
}

/* Sidebar navigation */
[data-testid="stSidebarNav"] a {
    border-radius: 10px;
    margin-bottom: 8px;
}

/* Navigation hover */
[data-testid="stSidebarNav"] a:hover {
    background-color: #406E8E;
}

/* Headings */
h1, h2, h3 {
    color: #23395B !important;
}

/* Buttons */
.stButton > button {
    background-color: #406E8E;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 1rem;
    transition: 0.2s ease;
}

/* Button hover */
.stButton > button:hover {
    background-color: #23395B;
    color: white;
    border: none;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #DCE3EA;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 3px 12px rgba(35, 57, 91, 0.06);
}

/* Horizontal divider */
hr {
    border-color: #DCE3EA;
}
/* Top header bar */
[data-testid="stHeader"] {
    background-color: #F8FAFC;
}

/* Top toolbar icons */
[data-testid="stToolbar"] button {
    color: #23395B;
}

/* Deploy button */
[data-testid="stAppDeployButton"] {
    background-color: #406E8E;
    color: #FFFFFF;
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)



# Application pages

welcome = st.Page(
    "pages/welcome.py",
    title="Welcome",
    default=True
)

dashboard = st.Page(
    "pages/dashboard.py",
    title="Dashboard",
    icon="🏠",
    default=True
)

create_project = st.Page(
    "pages/create_project.py",
    title="Create Project",
    icon="➕"
)

project_history = st.Page(
    "pages/project_history.py",
    title="Project History",
    icon="🕘"
)

document_upload = st.Page(
    "pages/document_upload.py",
    title="Document Upload",
    icon="📁"
)

project_analysis = st.Page(
    "pages/project_analysis.py",
    title="Project Analysis",
    icon="📊"
)
team_management = st.Page(
    "pages/team_management.py",
    title="Team Management",
    icon="👥"
)
member_exit = st.Page(
    "pages/member_exit.py",
    title="Member Exit",
    icon="👤"
)

reports = st.Page(
    "pages/reports.py",
    title="Reports",
    icon="📄"
)


# Navigation

# Navigation

if st.session_state.get("entered_workspace", False):

    pg = st.navigation([
        dashboard,
        create_project,
        project_history,
        team_management,
        document_upload,
        project_analysis,
        member_exit,
        reports
    ])

else:

    pg = st.navigation(
        [welcome],
        position="hidden"
    )

pg.run()
