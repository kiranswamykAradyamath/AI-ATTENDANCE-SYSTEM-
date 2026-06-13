import streamlit as st
from urllib.parse import parse_qs, urlparse

from src.database.db import enroll_student_to_subject, find_subject_by_code, is_student_enrolled


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
    subject = _find_subject(join_code)
    if not subject:
        st.error("No subject found with this code")
        return

    student_id = _get_student_id()
    if not student_id:
        st.error("Please log in again before enrolling.")
        return

    if _is_enrolled(student_id, subject["subject_id"]):
        st.warning("You are already enrolled in this subject")
        return

    enroll_student_to_subject(student_id, subject["subject_id"])
    st.success("Successfully enrolled!")
    st.rerun()


@st.dialog("Enroll in Subject")
def enroll_dialog():
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

    subject = _find_subject(join_code)
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

    if _is_enrolled(student_id, subject["subject_id"]):
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
                enroll_student_to_subject(student_id, subject["subject_id"])
            st.markdown(
                '<div style="background-color: #dcfce7; border-left: 4px solid #22c55e; padding: 12px; border-radius: 4px; text-align: center;">'
                '<span style="color: #15803d; font-weight: 600;">✅ Successfully enrolled in ' + subject['name'] + '!</span>'
                '</div>',
                unsafe_allow_html=True
            )
            _clear_subject_query()
            st.rerun()
