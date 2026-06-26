import streamlit as st
from urllib.parse import parse_qs, urlparse

from src.database.db import DatabaseConnectionError, enroll_student_to_subject, find_subject_by_code, is_student_enrolled


def _get_student_id():
    student_data = st.session_state.get("student_data", {})
    if isinstance(student_data, dict):
        return student_data.get("student_id")
    return st.session_state.get("student_id")


def _find_subject(subject_code):
    return find_subject_by_code(subject_code)


def _validate_subject_code(code):
    """Validate and provide feedback on subject code format."""
    code = (code or "").strip().upper()
    if not code:
        return False, "Please enter a subject code"
    if len(code) < 3:
        return False, "Subject code must be at least 3 characters"
    return True, code


def _extract_join_code_from_link(join_link):
    join_link = (join_link or "").strip()
    if not join_link:
        return None

    parsed = urlparse(join_link)
    query = parse_qs(parsed.query)
    join_code = (
        query.get("join-code", [None])[0]
        or query.get("subject", [None])[0]
    )

    if join_code:
        return join_code.strip().upper()

    return None


def _is_enrolled(student_id, subject_id):
    return is_student_enrolled(student_id, subject_id)


def _clear_subject_query():
    st.query_params.clear()


def _enroll_with_code(join_code):
    try:
        subject = _find_subject(join_code)
    except DatabaseConnectionError as exc:
        st.error(str(exc))
        return

    if not subject:
        st.error("No subject found with this code")
        return

    student_id = _get_student_id()
    if not student_id:
        st.error("Please log in again before enrolling.")
        return

    try:
        if _is_enrolled(student_id, subject["subject_id"]):
            st.warning("You are already enrolled in this subject")
            return

        enroll_student_to_subject(student_id, subject["subject_id"])
    except DatabaseConnectionError as exc:
        st.error(str(exc))
        return
    st.success("Successfully enrolled!")
    st.rerun()


def _apply_dialog_styles():
    st.markdown(
        """
        <style>
        /* Dialog Modal Box Styling */
        div[data-testid="stDialog"] > div[role="dialog"] {
            border-radius: 24px !important;
            background-color: #ffffff !important;
            padding: 1.5rem !important;
        }
        
        /* Remove default border line under tabs in Streamlit */
        div[data-testid="stDialog"] div[data-testid="stTabs"] [role="tablist"] {
            border-bottom: none !important;
            gap: 8px !important;
        }
        
        /* Style individual tab buttons */
        div[data-testid="stDialog"] div[data-testid="stTabs"] button[data-baseweb="tab"] {
            font-family: 'Google Sans', sans-serif !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            color: #4b5563 !important;
            background-color: #f1f5f9 !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 999px !important;
            padding: 0.5rem 1.25rem !important;
            margin-right: 0.25rem !important;
            transition: all 0.2s ease-in-out !important;
        }
        
        /* Active tab style */
        div[data-testid="stDialog"] div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
            color: #ffffff !important;
            background-color: #5865f2 !important;
            border-color: #5865f2 !important;
            box-shadow: 0 4px 10px rgba(88, 101, 242, 0.25) !important;
        }
        
        /* Hover tab style */
        div[data-testid="stDialog"] div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
            color: #1e293b !important;
            background-color: #e2e8f0 !important;
            border-color: #cbd5e1 !important;
        }
        
        /* Active hover tab style */
        div[data-testid="stDialog"] div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"]:hover {
            color: #ffffff !important;
            background-color: #4752d9 !important;
        }
        
        /* Text inputs styling */
        div[data-testid="stDialog"] div[data-testid="stTextInput"] label {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            color: #374151 !important;
            margin-bottom: 0.4rem !important;
        }
        
        div[data-testid="stDialog"] div[data-testid="stTextInput"] input {
            border: 1.5px solid #cbd5e1 !important;
            border-radius: 12px !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 500 !important;
            padding: 0.65rem 1rem !important;
            background-color: #f8fafc !important;
            color: #0f172a !important;
            transition: all 0.2s ease-in-out !important;
        }
        
        div[data-testid="stDialog"] div[data-testid="stTextInput"] input:focus {
            border-color: #5865f2 !important;
            box-shadow: 0 0 0 3px rgba(88, 101, 242, 0.18) !important;
            background-color: #ffffff !important;
        }
        
        /* Primary Button Styling */
        div[data-testid="stDialog"] button[kind="primary"] {
            background-color: #5865f2 !important;
            border: none !important;
            border-radius: 999px !important;
            color: #ffffff !important;
            font-family: 'Google Sans', sans-serif !important;
            font-weight: 800 !important;
            padding: 0.75rem 1.4rem !important;
            transition: all 0.25s ease-in-out !important;
            margin-top: 1rem !important;
            width: 100% !important;
        }
        
        div[data-testid="stDialog"] button[kind="primary"]:hover {
            background-color: #4752d9 !important;
            transform: scale(1.02) !important;
            box-shadow: 0 4px 12px rgba(88, 101, 242, 0.25) !important;
        }
        
        /* Secondary Button Styling */
        div[data-testid="stDialog"] button[kind="secondary"] {
            background-color: #f1f5f9 !important;
            color: #475569 !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 999px !important;
            font-family: 'Google Sans', sans-serif !important;
            font-weight: 800 !important;
            padding: 0.75rem 1.4rem !important;
            transition: all 0.25s ease-in-out !important;
            width: 100% !important;
        }
        
        div[data-testid="stDialog"] button[kind="secondary"]:hover {
            background-color: #e2e8f0 !important;
            color: #1e293b !important;
            transform: scale(1.02) !important;
        }
        
        /* Help texts / description */
        div[data-testid="stDialog"] p {
            font-family: 'Outfit', sans-serif !important;
            font-size: 0.95rem !important;
            color: #4b5563 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.dialog("Enroll in Subject")
def enroll_dialog():
    _apply_dialog_styles()
    code_tab, link_tab = st.tabs(["Subject Code", "Share Link"])

    with code_tab:
        st.write("Enter the subject code shared by your teacher to enroll.")
        join_code = st.text_input("Subject Code", placeholder="Eg.CS101")

        if st.button("Enroll Now", type="primary", width="stretch", key="enroll_by_code"):
            is_valid, result = _validate_subject_code(join_code)
            if not is_valid:
                st.warning(result)
                return
            _enroll_with_code(result)

    with link_tab:
        st.write("Paste the share link sent by your teacher.")
        join_link = st.text_input(
            "Share Link",
            placeholder="https://your-app.streamlit.app/?join-code=CS101",
        )

        if st.button("Enroll Using Link", type="primary", width="stretch", key="enroll_by_link"):
            join_code = _extract_join_code_from_link(join_link)
            if not join_code:
                st.warning("Please paste a valid subject share link")
                return
            _enroll_with_code(join_code)


@st.dialog("Quick Enrollment")
def auto_enroll_dialog(join_code):
    _apply_dialog_styles()
    student_id = _get_student_id()
    if not student_id:
        st.markdown(
            '<div style="background-color: #fee2e2; border-left: 4px solid #dc2626; padding: 12px; border-radius: 4px;">'
            '<span style="color: #991b1b; font-weight: 500;">❌ Please log in before enrolling.</span>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("Close", type="secondary", key="close_login_required"):
            _clear_subject_query()
            st.rerun()
        return

    try:
        subject = _find_subject(join_code)
    except DatabaseConnectionError as exc:
        st.error(str(exc))
        if st.button("Close", type="secondary", key="close_connection_error"):
            _clear_subject_query()
            st.rerun()
        return

    if not subject:
        st.markdown(
            '<div style="background-color: #fee2e2; border-left: 4px solid #dc2626; padding: 12px; border-radius: 4px; text-align: center;">'
            '<span style="color: #991b1b; font-weight: 500;">❌ Subject not found.</span>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div style="color: #666; font-size: 0.9rem; text-align: center; margin-top: 8px;">'
            'The subject code "' + (join_code or "").strip().upper() + '" does not exist. Please verify with your teacher.'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown("")
        if st.button("Try Again", type="secondary", use_container_width=True, key="close_invalid_code"):
            _clear_subject_query()
            st.rerun()
        return

    try:
        already_enrolled = _is_enrolled(student_id, subject["subject_id"])
    except DatabaseConnectionError as exc:
        st.error(str(exc))
        if st.button("Close", type="secondary", key="close_connection_error_2"):
            _clear_subject_query()
            st.rerun()
        return

    if already_enrolled:
        st.markdown(
            '<div style="background-color: #dbeafe; border-left: 4px solid #0284c7; padding: 12px; border-radius: 4px; text-align: center;">'
            '<span style="color: #0c4a6e; font-weight: 500;">ℹ️ You are already enrolled in ' + subject['name'] + '.</span>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown("")
        if st.button("Got it", type="secondary", use_container_width=True, key="already_enrolled"):
            _clear_subject_query()
            st.rerun()
        return

    st.markdown(
        '<div style="padding: 16px; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 8px; margin: 12px 0; border: 1px solid #bae6fd; text-align: center;">'
        '<span style="color: #0369a1; font-weight: 600; font-size: 1rem;">'
        f'Would you like to enroll in <strong>{subject["name"]}</strong>?'
        '</span></div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2, gap="small")
    with col1:
        if st.button("No Thanks", type="secondary", width="stretch", key="no_thanks"):
            _clear_subject_query()
            st.rerun()

    with col2:
        if st.button("Yes Enroll Now", type="primary", width="stretch", key="yes_enroll"):
            with st.spinner("Enrolling..."):
                try:
                    enroll_student_to_subject(student_id, subject["subject_id"])
                except DatabaseConnectionError as exc:
                    st.error(str(exc))
                    return
            st.markdown(
                '<div style="background-color: #dcfce7; border-left: 4px solid #22c55e; padding: 12px; border-radius: 4px; text-align: center;">'
                '<span style="color: #15803d; font-weight: 600;">✅ Successfully enrolled in ' + subject['name'] + '!</span>'
                '</div>',
                unsafe_allow_html=True
            )
            _clear_subject_query()
            st.rerun()
