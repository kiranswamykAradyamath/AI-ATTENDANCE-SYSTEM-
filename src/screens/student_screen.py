import hashlib

import streamlit as st
from src.screens.components.subject_card import subject_card
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.screens.components.header import header_dashboard
from src.screens.components.fotter import fotter_dashboard
from src.database.db import DatabaseConnectionError, get_all_students, create_student,get_student_subjects, get_student_attendance,unenroll_student_to_subject
from src.screens.components.dialog_auto_enroll import enroll_dialog
from src.ui.navigation import clear_student_transient_state, navigate_to


def _uploaded_file_hash(uploaded_file):
    return hashlib.sha256(uploaded_file.getvalue()).hexdigest()


def _get_student_scan_result(photo_source):
    photo_hash = _uploaded_file_hash(photo_source)
    if (
        st.session_state.get("student_scan_hash") == photo_hash
        and "student_scan_result" in st.session_state
    ):
        return st.session_state["student_scan_result"]

    import numpy as np
    from PIL import Image

    from src.pipelines.face_pipelines import predict_attendence

    img = np.array(Image.open(photo_source))

    # Wrap pipeline call — catches DatabaseConnectionError, DeepFace ValueError,
    # and any other unexpected exception so the app never hard-crashes.
    try:
        detected, _, num_faces = predict_attendence(img)
    except DatabaseConnectionError:
        raise  # re-raise so caller can show DB-specific help message
    except Exception as exc:
        raise RuntimeError(
            f"Face recognition pipeline error: {exc}. "
            "The model may still be loading — please try again in a moment."
        ) from exc

    result = {
        "photo_hash": photo_hash,
        "detected": detected,
        "num_faces": num_faces,
        "student": None,
        "missing_record": False,
    }

    if detected:
        student_id = list(detected.keys())[0]
        all_students = get_all_students() or []
        student = next((s for s in all_students if s["student_id"] == student_id), None)
        if student:
            result["student"] = student
        else:
            result["missing_record"] = True

    st.session_state["student_scan_hash"] = photo_hash
    st.session_state["student_scan_result"] = result
    return result


def student_dashboard():
    st.markdown(
        """
        <style>
        .student-dashboard-shell {
            padding: 0.5rem 0 1.5rem;
        }

        .student-top-actions {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 0.75rem;
        }

        .student-subjects-title {
            color: #2d3042 !important;
            font-family: 'Google Sans', sans-serif !important;
            font-size: 2.7rem !important;
            font-weight: 900 !important;
            line-height: 0.82 !important;
            letter-spacing: 0 !important;
            margin: 0 !important;
        }

        .student-section-rule {
            border-top: 1px solid rgba(31, 41, 55, 0.18);
            margin: 2.1rem 0 1.7rem;
        }

        .subject-card {
            background: #ffffff !important;
            border: 1.5px solid #3f3f46;
            border-radius: 18px;
            padding: 1.55rem 1.4rem 1.35rem;
            margin: 0 0 1rem;
            box-shadow: none;
            min-height: 156px;
        }

        .subject-card h3 {
            color: #2f3142 !important;
            font-family: 'Google Sans', sans-serif !important;
            font-size: 1.25rem !important;
            font-weight: 850 !important;
            line-height: 1.25 !important;
            margin: 0 0 1.3rem !important;
        }

        .subject-link-icon {
            color: #9ca3af;
            font-size: 0.78rem;
            margin-left: 0.35rem;
            vertical-align: middle;
        }

        .subject-meta {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.35rem;
            color: #5e6377;
            font-size: 0.95rem;
            margin-bottom: 0.95rem;
        }

        .subject-meta strong {
            background: #e7e4ff;
            border-radius: 5px;
            color: #6a63db;
            font-weight: 850;
            padding: 0.18rem 0.45rem;
        }

        .subject-divider {
            color: #a1a1aa;
        }

        .subject-stats {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.75rem;
        }

        .subject-stat-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.18rem;
            border-radius: 7px;
            background: #f7f1fb;
            color: #3f3f46;
            padding: 0.28rem 0.5rem;
            font-size: 0.78rem;
            font-weight: 650;
        }

        .subject-stat-chip strong {
            color: #27272a;
            font-weight: 850;
        }

        .student-empty-subjects {
            background: #ffffff;
            border: 1.5px dashed #a4a7c5;
            border-radius: 18px;
            color: #3f3f46;
            font-weight: 750;
            padding: 1.4rem;
        }

        div[data-testid="stHorizontalBlock"]:has(.student-subjects-title) {
            align-items: center;
            transform: none !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.student-header-action-marker) {
            align-items: center;
            transform: none !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.student-subjects-title) div[data-testid="stColumn"],
        div[data-testid="stHorizontalBlock"]:has(.student-header-action-marker) div[data-testid="stColumn"],
        div[data-testid="stHorizontalBlock"]:has(.subject-card) div[data-testid="stColumn"] {
            background: transparent !important;
            border-radius: 0 !important;
            padding: 0 !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.subject-card) {
            transform: none !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.student-header-action-marker) div[data-testid="stButton"] > button[kind="secondary"] {
            background-color: #222222 !important;
            border: none !important;
            border-radius: 999px !important;
            color: #ffffff !important;
            font-weight: 800 !important;
            padding: 0.75rem 1.4rem !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.student-subjects-title) div[data-testid="stButton"] > button[kind="primary"] {
            background-color: #5865f2 !important;
            border: none !important;
            border-radius: 999px !important;
            color: #ffffff !important;
            font-weight: 800 !important;
            padding: 0.75rem 1.4rem !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.subject-card) div[data-testid="stButton"] > button[kind="tertiary"] {
            background-color: #000000 !important;
            border: none !important;
            border-radius: 999px !important;
            color: #ffffff !important;
            font-weight: 800 !important;
            margin: 0.05rem 0 1.1rem !important;
            padding: 0.72rem 1.2rem !important;
            width: 100% !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.student-header-action-marker) div[data-testid="stButton"] > button[kind="secondary"] *,
        div[data-testid="stHorizontalBlock"]:has(.student-subjects-title) div[data-testid="stButton"] > button[kind="primary"] *,
        div[data-testid="stHorizontalBlock"]:has(.subject-card) div[data-testid="stButton"] > button[kind="tertiary"] * {
            color: #ffffff !important;
            fill: #ffffff !important;
            font-weight: 800 !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.student-header-action-marker) div[data-testid="stButton"] > button[kind="secondary"]:hover {
            background-color: #111111 !important;
            color: #ffffff !important;
            transform: translateY(-1px) !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.student-subjects-title) div[data-testid="stButton"] > button[kind="primary"]:hover {
            background-color: #4752d9 !important;
            color: #ffffff !important;
            transform: translateY(-1px) !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.subject-card) div[data-testid="stButton"] > button[kind="tertiary"]:hover {
            background-color: #18181b !important;
            color: #ffffff !important;
            transform: translateY(-1px) !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.student-header-action-marker) div[data-testid="stButton"] > button:disabled,
        div[data-testid="stHorizontalBlock"]:has(.student-subjects-title) div[data-testid="stButton"] > button:disabled,
        div[data-testid="stHorizontalBlock"]:has(.subject-card) div[data-testid="stButton"] > button:disabled {
            background-color: #71717a !important;
            color: #ffffff !important;
            cursor: not-allowed !important;
            opacity: 0.72 !important;
            transform: none !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.student-header-action-marker) div[data-testid="stButton"] > button:disabled *,
        div[data-testid="stHorizontalBlock"]:has(.student-subjects-title) div[data-testid="stButton"] > button:disabled *,
        div[data-testid="stHorizontalBlock"]:has(.subject-card) div[data-testid="stButton"] > button:disabled * {
            color: #ffffff !important;
            fill: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    header_col, logout_col = st.columns([4.2, 1], vertical_alignment="center")
    with header_col:
        header_dashboard()
    with logout_col:
        st.markdown('<div class="student-header-action-marker"></div>', unsafe_allow_html=True)
        if st.button("Logout", key="student_logout_btn", type="secondary", width="stretch"):
            st.session_state['is_logged_in'] = False
            if "student_data" in st.session_state:
                del st.session_state.student_data
            clear_student_transient_state()
            st.rerun()

    student_data = st.session_state.get("student_data", {})
    student_id = student_data.get("student_id") if isinstance(student_data, dict) else None

    title_col, action_col = st.columns([1.35, 0.65], vertical_alignment="center", gap="large")
    with title_col:
        st.markdown('<h1 class="student-subjects-title">Your Enrolled<br>Subjects</h1>', unsafe_allow_html=True)

    with action_col:
        if st.button('Enroll in Subject', type='primary', width="stretch"):
            enroll_dialog()

    st.markdown('<div class="student-section-rule"></div>', unsafe_allow_html=True)

    subjects = []
    logs = []
    with st.spinner("Loading your subjects..."):
        try:
            subjects = get_student_subjects(student_id) or []
            logs = get_student_attendance(student_id) or []
        except DatabaseConnectionError as exc:
            st.error(str(exc))
            fotter_dashboard()
            return

    stats_map = {}
    for log in logs:
        if not isinstance(log, dict):
            continue
        subject_id = log.get('subject_id')
        if subject_id is None:
            continue
        stats_map[subject_id] = stats_map.get(subject_id, {'total_sessions': 0, 'attended_sessions': 0})
        stats_map[subject_id]['total_sessions'] += 1
        if log.get('is_present'):
            stats_map[subject_id]['attended_sessions'] += 1

    valid_subjects = []
    for sub_node in subjects:
        if not isinstance(sub_node, dict):
            continue

        subject = sub_node.get('subjects') or sub_node.get('subject') or sub_node
        if not isinstance(subject, dict):
            continue

        subject_id = subject.get('subject_id')
        name = subject.get('name')
        subject_code = subject.get('subject_code')
        section = subject.get('section')

        if not all([subject_id, name, subject_code, section]):
            continue

        valid_subjects.append({
            'subject_id': subject_id,
            'name': name,
            'subject_code': subject_code,
            'section': section,
        })

    if not valid_subjects:
        st.markdown('<div class="student-empty-subjects">No enrolled subjects found. Enroll in a subject to see it here.</div>', unsafe_allow_html=True)
        fotter_dashboard()
        return

    cols = st.columns(2, gap="large")
    for i, subject in enumerate(valid_subjects):
        subject_id = subject['subject_id']
        stats = stats_map.get(subject_id, {"total_sessions": 0, "attended_sessions": 0})

        def unenroll_btn(subject_id=subject_id):
            if st.button("Unenroll from this course", key=f'unenroll_{subject_id}', type="tertiary", width="stretch", icon=":material/delete_forever:"):
                try:
                    unenroll_student_to_subject(student_id, subject_id)
                    st.toast('Unenrolled from subject')
                    st.rerun()
                except DatabaseConnectionError as exc:
                    st.error(str(exc))

        with cols[i % 2]:
            subject_card(
                name=subject['name'],
                subject_code=subject['subject_code'],
                section=subject['section'],
                stats=[
                    ("Total", stats['total_sessions']),
                    ("Attended", stats['attended_sessions']),
                ],
                fotter_callback=unenroll_btn,
            )

    fotter_dashboard()

def student_screen():

    style_background_dashboard()
    style_base_layout()

    # Test Bypass to easily log in as a student using query params
    test_student_id = st.query_params.get("test-student")
    if test_student_id:
        try:
            student_id_val = int(test_student_id)
            from src.database.db import get_all_students
            all_students = get_all_students() or []
            student = next((s for s in all_students if s["student_id"] == student_id_val), None)
            if student:
                st.session_state.is_logged_in = True
                st.session_state.user_role = 'student'
                st.session_state.student_data = student
                st.query_params.clear()
                st.rerun()
        except Exception:
            pass

    if "student_data" in st.session_state :
        student_dashboard()
        return

    # ── Custom CSS for Alignment ──────────────────────────────────────────
    st.markdown("""
        <style>
        /* Force the app background color to match the light lavender theme in the screenshot */
        .stApp {
            background-color: #E2E6FA !important;
        }

        /* Prevent global negative translation from clipping content on the left */
        .stApp div[data-testid="stHorizontalBlock"] {
            transform: none !important;
        }

        /* Ensure the login title matches the image's clean bold look */
        .portal-title {
            text-align: center;
            font-family: 'Google Sans', sans-serif;
            font-weight: 800;
            font-size: clamp(1.75rem, 3vw, 2.5rem);
            line-height: 1.05;
            margin: 0;
            color: #1f2937;
        }

        .student-card-subtitle {
            color: #6b7280;
            font-size: clamp(0.9rem, 1.6vw, 1rem);
            font-weight: 600;
            line-height: 1.35;
            margin: 0.7rem auto 1.3rem;
            max-width: 28rem;
            text-align: center;
        }

        .student-login-marker {
            display: block;
            width: 100%;
        }

        /* Ensure all spacer and alignment columns on the login page are transparent */
        div[data-testid="stHorizontalBlock"]:has(.student-login-marker) div[data-testid="stColumn"]:not(:has(.student-login-marker)) {
            background: transparent !important;
            border-radius: 0 !important;
            padding: 0 !important;
            box-shadow: none !important;
        }
        
        div[data-testid="stHorizontalBlock"]:has(.student-login-back-marker) div[data-testid="stColumn"] {
            background: transparent !important;
            border-radius: 0 !important;
            padding: 0 !important;
            box-shadow: none !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.student-login-header-marker) div[data-testid="stColumn"] {
            background: transparent !important;
            border-radius: 0 !important;
            padding: 0 !important;
            box-shadow: none !important;
        }

        /* Apply white card styles ONLY to the column containing the card itself */
        div[data-testid="stColumn"]:has(.student-login-marker) {
            background: #ffffff !important;
            padding: clamp(1.5rem, 3.5vw, 3rem) !important;
            border-radius: 2rem !important;
            min-width: 0 !important;
            box-shadow: 0 20px 40px rgba(31, 41, 55, 0.06) !important;
        }

        div[data-testid="stColumn"]:has(.student-login-marker) p {
            font-size: clamp(0.78rem, 1.4vw, 0.95rem) !important;
            line-height: 1.25 !important;
            margin-bottom: 0.4rem !important;
        }

        /* Remove default Streamlit camera borders and background */
        div[data-testid="stColumn"]:has(.student-login-marker) div[data-testid="stCameraInput"] {
            width: 100% !important;
            max-width: min(620px, 100%) !important;
            margin: 0 auto !important;
            position: relative !important;
            overflow: hidden !important;
            border-radius: 1.25rem !important;
            background: transparent !important;
        }

        div[data-testid="stColumn"]:has(.student-login-marker) div[data-testid="stCameraInput"] > div {
            border: none !important;
            background: transparent !important;
            padding: 0 !important;
            box-shadow: none !important;
        }

        div[data-testid="stColumn"]:has(.student-login-marker) div[data-testid="stCameraInput"] video,
        div[data-testid="stColumn"]:has(.student-login-marker) div[data-testid="stCameraInput"] img,
        div[data-testid="stColumn"]:has(.student-login-marker) div[data-testid="stCameraInput"] canvas {
            width: 100% !important;
            max-height: min(52vh, 430px) !important;
            aspect-ratio: 16 / 9 !important;
            object-fit: cover !important;
            object-position: center center !important;
            border-radius: 18px !important;
            background: transparent !important;
        }

        /* Pill-shaped deep purple/magenta button with stacked lines */
        div[data-testid="stColumn"]:has(.student-login-marker) div[data-testid="stCameraInput"] button {
            width: min(28rem, 100%) !important;
            min-height: 4.2rem !important;
            margin: 1.25rem auto 0 !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            border-radius: 999px !important;
            background: #7c008c !important;
            padding: 0.6rem 1.5rem !important;
            white-space: normal !important;
            overflow: visible !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(124, 0, 140, 0.25) !important;
            transition: all 0.2s ease-in-out !important;
        }

        div[data-testid="stColumn"]:has(.student-login-marker) div[data-testid="stCameraInput"] button:hover {
            background: #620070 !important;
            transform: scale(1.02) !important;
            box-shadow: 0 6px 16px rgba(124, 0, 140, 0.35) !important;
        }

        /* Style the main button text ("Take Photo") */
        div[data-testid="stColumn"]:has(.student-login-marker) div[data-testid="stCameraInput"] button p,
        div[data-testid="stColumn"]:has(.student-login-marker) div[data-testid="stCameraInput"] button span {
            color: #ffffff !important;
            font-size: 1.15rem !important;
            font-weight: 800 !important;
            margin: 0 !important;
            line-height: 1.2 !important;
        }

        /* Add the subtitle line to the button */
        div[data-testid="stColumn"]:has(.student-login-marker) div[data-testid="stCameraInput"] button::after {
            content: "Verify Face & Mark Attendance" !important;
            color: rgba(255, 255, 255, 0.85) !important;
            display: block !important;
            font-size: 0.82rem !important;
            font-weight: 700 !important;
            margin-top: 3px !important;
            text-align: center !important;
            width: 100% !important;
        }

        div[data-testid="stColumn"]:has(.student-login-marker) div[data-testid="stVerticalBlockBorderWrapper"] {
            max-width: min(760px, 100%) !important;
            margin: 1rem auto 0 !important;
        }

        /* Header Navigation Back-to-Home block styling */
        div[data-testid="stHorizontalBlock"]:has(.student-login-back-marker) {
            align-items: center !important;
            margin-top: -0.4rem !important;
            margin-bottom: clamp(0.8rem, 2.5vh, 1.6rem) !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.student-login-back-marker) div[data-testid="stColumn"] {
            background: transparent !important;
            padding: 0 !important;
            border-radius: 0 !important;
        }

        /* Back to Home Button Styling */
        div[data-testid="stHorizontalBlock"]:has(.student-login-back-marker) button {
            background-color: #1f2937 !important;
            color: #ffffff !important;
            border-radius: 999px !important;
            font-size: 0.9rem !important;
            font-weight: 700 !important;
            padding: 0.6rem 1.6rem !important;
            border: none !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
            transition: all 0.2s ease-in-out !important;
            width: auto !important;
            display: inline-flex !important;
            margin-left: auto !important;
            margin-right: 0 !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.student-login-back-marker) button * {
            color: #ffffff !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.student-login-back-marker) button:hover {
            background-color: #111827 !important;
            transform: scale(1.03) !important;
        }

        .student-camera-instruction-top {
            text-align: center !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            color: #1f2937 !important;
            margin-top: 0.5rem !important;
            margin-bottom: 0.85rem !important;
        }

        .student-camera-status {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.55rem;
            color: #1f2937;
            font-weight: 800;
            margin-top: 1rem;
        }

        .student-camera-status-dot {
            width: 0.62rem;
            height: 0.62rem;
            border-radius: 999px;
            background: #22c55e;
            box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.14);
        }

        .student-camera-instruction,
        .student-privacy-note {
            color: #6b7280 !important;
            font-size: 0.9rem !important;
            line-height: 1.35 !important;
            text-align: center !important;
            margin: 0.65rem auto 0 !important;
        }

        .student-privacy-note {
            margin-top: 1rem !important;
            font-weight: 700 !important;
        }

        div[data-testid="stAlert"] {
            border-radius: 8px;
            border: none;
        }

        .student-info-text {
            background: #ffffff;
            border-radius: 8px;
            color: #222222 !important;
            font-weight: 800 !important;
            margin: 0.75rem 0;
            padding: 0.85rem 1rem;
        }

        /* Register profile container styling */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.register-title) {
            background-color: #f9fafb !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 1rem !important;
            padding: 1.5rem !important;
            margin-top: 1.5rem !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02) !important;
        }

        .register-title {
            color: #1f2937 !important;
            font-family: 'Google Sans', sans-serif !important;
            font-size: 1.5rem !important;
            font-weight: 800 !important;
            margin-bottom: 1rem !important;
        }

        .voice-note {
            background-color: #f3e8ff !important;
            color: #6b21a8 !important;
            border-radius: 0.5rem !important;
            font-weight: 600 !important;
            margin: 0.5rem 0 1rem 0 !important;
            padding: 0.75rem 1rem !important;
            font-size: 0.9rem !important;
        }

        /* Register button styling */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.register-title) div[data-testid="stButton"] button {
            background-color: #7c008c !important;
            color: white !important;
            border: none !important;
            border-radius: 999px !important;
            font-weight: 800 !important;
            padding: 0.65rem 1.6rem !important;
            box-shadow: 0 4px 12px rgba(124, 0, 140, 0.2) !important;
            transition: all 0.2s ease-in-out !important;
            width: 100% !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.register-title) div[data-testid="stButton"] button:hover {
            background-color: #620070 !important;
            transform: scale(1.02) !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stAudioInput"] {
            border-radius: 8px !important;
        }

        @media (max-width: 760px) {
            div[data-testid="stColumn"]:has(.student-login-marker) {
                padding: 1rem !important;
                border-radius: 1.15rem !important;
            }

            .portal-title {
                margin-top: 0;
            }

            div[data-testid="stColumn"]:has(.student-login-marker) div[data-testid="stCameraInput"] video,
            div[data-testid="stColumn"]:has(.student-login-marker) div[data-testid="stCameraInput"] img,
            div[data-testid="stColumn"]:has(.student-login-marker) div[data-testid="stCameraInput"] canvas {
                max-height: 42vh !important;
            }

            div[data-testid="stColumn"]:has(.student-login-back-marker) div[data-testid="stButton"],
            div[data-testid="stColumn"]:has(.student-login-back-marker) button {
                width: 100% !important;
                margin-left: 0 !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # ── Top Section: Logo & Brand + Navigation (Aligned Horizontally) ───────
    header_col, back_col = st.columns([3.8, 1.2], vertical_alignment="center")
    with header_col:
        st.markdown('<span class="student-login-header-marker"></span>', unsafe_allow_html=True)
        header_dashboard()
    with back_col:
        st.markdown('<span class="student-login-back-marker"></span>', unsafe_allow_html=True)
        if st.button("Back To Home", type="secondary", width="stretch", key="student_back_home_btn"):
            navigate_to(None)

    _, login_col, _ = st.columns([0.16, 0.68, 0.16])
    with login_col:
        st.markdown('<span class="student-login-marker"></span>', unsafe_allow_html=True)
        st.markdown('<div class="portal-title">Login using FaceID</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="student-card-subtitle">Verify your identity to mark today\'s attendance.</div>',
            unsafe_allow_html=True,
        )

        # Instruction above camera
        st.markdown('<div class="student-camera-instruction-top">Position your face inside the frame.</div>', unsafe_allow_html=True)
        photo_source = st.camera_input("Biometric Scan", label_visibility="collapsed", key="student_login_camera")
        st.markdown(
            """
            <div class="student-camera-status">
                <span class="student-camera-status-dot"></span>
                <span>Camera Ready</span>
            </div>
            <div class="student-camera-instruction">Make sure your face is clearly visible and lighting is good.</div>
            <div class="student-privacy-note">Secure verification. Face data is used only for attendance.</div>
            """,
            unsafe_allow_html=True,
        )

        show_registration = False
        if photo_source:
            with st.spinner("AI is Scanning.."):
                try:
                    scan_result = _get_student_scan_result(photo_source)
                except DatabaseConnectionError as exc:
                    st.error(str(exc))
                    st.info("Face login needs the students table from Supabase before it can compare faces.")
                    fotter_dashboard()
                    return
                except RuntimeError as exc:
                    st.error(str(exc))
                    fotter_dashboard()
                    return
                except Exception as exc:
                    st.error(
                        f"Unexpected error during face scan: {exc}\n\n"
                        "Please refresh the page and try again."
                    )
                    fotter_dashboard()
                    return

                if scan_result["num_faces"] == 0:
                    st.warning("Faces not found!")
                elif scan_result["num_faces"] > 1:
                    st.warning("Multiple faces detected! Please ensure only one face is visible.")
                else:
                    if scan_result["student"]:
                        student = scan_result["student"]
                        st.success(f"Welcome back, {student['name']}!")
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f"Welcome Back! {student['name']}")
                        clear_student_transient_state()
                        st.rerun()
                    elif scan_result["missing_record"]:
                        st.markdown('<h4 class="student-info-text">Face matched an old cached ID, but no student record exists now. Please register again.</h4>', unsafe_allow_html=True)
                        show_registration = True
                    else:
                        st.markdown('<h4 class="student-info-text">Face not recognized! You might be a new student.</h4>', unsafe_allow_html=True)
                        show_registration = True

            if show_registration:
                with st.container(border = True):
                    st.markdown('<h2 class="register-title">Register new Profile</h2>', unsafe_allow_html=True)
                    new_name = st.text_input("Enter your name", placeholder="Your Name")

                    st.markdown("### Optional : Voice Enrollment")
                    st.markdown(
                        '<div class="voice-note">Enroll your for voice only attendance</div>',
                        unsafe_allow_html=True,
                    )

                    audio_data = None

                    try:
                        audio_data = st.audio_input("Record a short phrase like I am present, My name is Akash.")
                    except Exception as e:
                        st.error(f"Error accessing microphone: {e}")

                    if st.button('Create Account', type='primary'):

                        if new_name:
                            with st.spinner("Creating your account..."):
                                import numpy as np
                                from PIL import Image

                                from src.pipelines.face_pipelines import get_face_embeddings, train_classifier
                                from src.pipelines.voice_pipelines import get_voice_embedding

                                img = np.array(Image.open(photo_source))
                                encodings = get_face_embeddings(img)
                                if encodings:
                                    face_emb = encodings[0].tolist()
                                    voice_emb = None
                                    if audio_data:
                                        voice_emb = get_voice_embedding(audio_data.read())
                                    try:
                                        response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)
                                    except DatabaseConnectionError as exc:
                                        st.error(str(exc))
                                        return

                                    if response_data:
                                        train_classifier()
                                        st.session_state.is_logged_in = True
                                        st.session_state.user_role = 'student'
                                        st.session_state.student_data = response_data[0] if isinstance(response_data, list) else response_data
                                        st.toast(f"Welcome Back! {new_name}")
                                        clear_student_transient_state()
                                        st.rerun()
                                    else:
                                        st.error("could not capture your facial features for registartion")

                                else:
                                    st.warning("Could not capture your facial features for registration.")
                        else:
                            st.warning("Please enter your name!")



    fotter_dashboard()