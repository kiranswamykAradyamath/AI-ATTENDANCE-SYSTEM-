import streamlit as st


STUDENT_TRANSIENT_KEYS = (
    "student_login_camera",
    "student_scan_hash",
    "student_scan_result",
    "student_scan_error",
    "student_show_registration",
)

TEACHER_TRANSIENT_KEYS = (
    "dialog_cam",
    "dialog_upload",
    "dialog_cam_hash",
    "dialog_upload_hashes",
    "photo_tab",
    "voice_attendance_results",
)


def clear_keys(*keys):
    for key in keys:
        st.session_state.pop(key, None)


def clear_student_transient_state():
    clear_keys(*STUDENT_TRANSIENT_KEYS)


def clear_teacher_transient_state(clear_attendance_images=False):
    clear_keys(*TEACHER_TRANSIENT_KEYS)
    if clear_attendance_images:
        clear_keys("attendance_images")


def navigate_to(login_type):
    current_login_type = st.session_state.get("login_type")

    if current_login_type != "student" and login_type == "student":
        clear_student_transient_state()

    if current_login_type != "teacher" and login_type == "teacher":
        clear_teacher_transient_state(clear_attendance_images=True)

    if login_type is None:
        clear_student_transient_state()
        clear_teacher_transient_state(clear_attendance_images=True)

    st.session_state["login_type"] = login_type
    st.rerun()
