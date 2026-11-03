import textwrap
import streamlit as st

import streamlit as st
import base64
from pathlib import Path

# Load Welcome Page Background

image_path = Path(__file__).parent.parent / "assets" / "welcome-bg.png"

with open(image_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

# Background Styling

st.markdown(f"""
<style>

.stApp {{
    background-image:
        linear-gradient(
            rgba(248, 250, 252, 0.18),
            rgba(248, 250, 252, 0.18)
        ),
        url("data:image/png;base64,{encoded_image}");

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

</style>
""", unsafe_allow_html=True)

# Welcome Page
st.markdown("""
<style>

/* Hide default page spacing */
.block-container {
    padding-top: 3rem;
}

/* Welcome container */
.welcome-container {
    text-align: center;
    padding: 90px 20px 40px;
    max-width: 850px;
    margin: auto;
}

/* Brand */
.welcome-logo {
    font-size: 28px;
    font-weight: 700;
    color: #23395B;
    letter-spacing: 2px;
    margin-bottom: 55px;
}

/* Main heading */
.welcome-title {
    color: #23395B;
    font-size: 52px;
    font-weight: 750;
    line-height: 1.2;
    margin-bottom: 18px;
}

/* Subtitle */
.welcome-subtitle {
    color: #406E8E;
    font-size: 23px;
    font-weight: 500;
    margin-bottom: 18px;
}

/* Description */
.welcome-description {
    color: #3F4045;
    font-size: 16px;
    line-height: 1.8;
    max-width: 650px;
    margin: auto;
}

/* Button */
.stButton > button {
    background-color: #406E8E;
    color: white;
    border-radius: 10px;
    padding: 12px 28px;
    font-size: 16px;
    font-weight: 600;
    border: none;
}

</style>
""", unsafe_allow_html=True)



st.html("""
<div class="welcome-container">
    <div class="welcome-logo">
        ✧ &nbsp; KNOVIA
    </div>
    <div class="welcome-title">
        Where Knowledge Never Leaves.
    </div>
    <div class="welcome-subtitle">
        Your projects deserve continuity.
    </div>
    <div class="welcome-description">
        Preserve project knowledge, identify risks and ensure
        seamless team transitions with intelligent project memory.
    </div>
</div>
""")


col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("Explore Workspace →", use_container_width=True):
        st.session_state["entered_workspace"] = True
        st.rerun()