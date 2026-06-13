from datetime import datetime
import re

import streamlit as st

from src.screens.components.fotter import fotter_dashboard
from src.screens.components.header import header_dashboard
from src.screens.components.subject_card import subject_card
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.ui.navigation import clear_teacher_transient_state, navigate_to


def get_teacher_db():
    from src.database import db

    return db


def get_add_photos_dialog():
    from src.screens.components.dialog_add_photo import dialog_add_photo

    return dialog_add_photo


def get_attendance_result_dialog():
    from src.screens.components.dialog_attendance_result import attendance_result_dialog

    return attendance_result_dialog


def get_create_subject_dialog():
    from src.screens.components.dialog_create_subjects import create_subject_dialog

    return create_subject_dialog


def get_face_attendance_predictor():
    from src.pipelines.face_pipelines import predict_attendence

    return predict_attendence


def get_share_subject_dialog():
    from src.screens.components.dialog_share_subject import share_subject_dialog

    return share_subject_dialog


def get_voice_attendance_dialog():
    from src.screens.components.dialog_voice_attendance import voice_attendance_dialog

    return voice_attendance_dialog


def get_subject_students_loader():
    from src.database.db import get_enrolled_students_for_subject

    return get_enrolled_students_for_subject


@st.cache_data(ttl=10, show_spinner=False)
def cached_teacher_subjects(teacher_id):
    return get_teacher_db().get_teacher_subjects(teacher_id)


@st.cache_data(ttl=20, show_spinner=False)
def cached_teacher_attendance(teacher_id):
    return get_teacher_db().get_attendance_for_teacher(teacher_id) or []


def apply_custom_button_styles():
    st.markdown(
        """
        <style>
        div[data-testid="stColumn"]:has(.teacher-auth-marker) div[data-testid="stButton"] {
            width: 100% !important;
        }

        div[data-testid="stColumn"]:has(.teacher-auth-marker) div[data-testid="stButton"] > button {
            width: 100% !important;
            min-height: 2.75rem !important;
            border-radius: 0.45rem !important;
            transform: none !important;
        }

        div[data-testid="column"]:nth-of-type(1) button {
            background-color: #df2c8a !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
        }

        div[data-testid="column"]:nth-of-type(2) button {
            background-color: #5865f2 !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_teacher_auth_layout():
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1180px !important;
            min-height: 100vh !important;
            padding: clamp(1rem, 2.4vw, 1.8rem) clamp(1rem, 3vw, 2.2rem) 1rem !important;
        }

        .teacher-auth-marker {
            display: block;
            width: 100%;
        }

        div[data-testid="stColumn"]:has(.teacher-auth-marker) {
            background: transparent !important;
            padding: 0 !important;
            border-radius: 0 !important;
        }

        div[data-testid="stColumn"]:has(.teacher-auth-marker) h1,
        div[data-testid="stColumn"]:has(.teacher-auth-marker) h2,
        div[data-testid="stColumn"]:has(.teacher-auth-marker) h3 {
            font-size: clamp(2rem, 4vw, 3rem) !important;
            line-height: 1.05 !important;
            margin: 0 0 1.2rem !important;
        }

        div[data-testid="stColumn"]:has(.teacher-auth-marker) label,
        div[data-testid="stColumn"]:has(.teacher-auth-marker) p {
            font-size: 0.95rem !important;
            line-height: 1.25 !important;
        }

        div[data-testid="stColumn"]:has(.teacher-auth-marker) input {
            min-height: 2.75rem !important;
            font-size: 0.95rem !important;
        }

        div[data-testid="stColumn"]:has(.teacher-auth-marker) hr {
            margin: 1.35rem 0 !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.teacher-auth-actions-marker) {
            gap: 1rem !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.teacher-auth-actions-marker) div[data-testid="stColumn"] {
            background: transparent !important;
            padding: 0 !important;
            border-radius: 0 !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.teacher-back-marker) {
            align-items: center !important;
            margin-top: -0.5rem !important;
            margin-bottom: clamp(1.4rem, 5vh, 3rem) !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.teacher-back-marker) div[data-testid="stColumn"] {
            background: transparent !important;
            padding: 0 !important;
            border-radius: 0 !important;
        }

        div[data-testid="stColumn"]:has(.teacher-back-marker) div[data-testid="stButton"],
        div[data-testid="stColumn"]:has(.teacher-back-marker) button {
            width: min(11rem, 100%) !important;
            margin-left: auto !important;
        }

        @media (min-width: 1180px) {
            div[data-testid="stColumn"]:has(.teacher-auth-marker) {
                max-width: 760px !important;
            }
        }

        @media (max-width: 760px) {
            .block-container {
                padding: 0.9rem 0.9rem 1rem !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.teacher-back-marker) {
                margin-bottom: 1rem !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.teacher-auth-actions-marker) {
                flex-direction: column !important;
                gap: 0.7rem !important;
            }

            div[data-testid="stColumn"]:has(.teacher-back-marker) div[data-testid="stButton"],
            div[data-testid="stColumn"]:has(.teacher-back-marker) button {
                width: 100% !important;
                margin-left: 0 !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_teacher_login():
    apply_custom_button_styles()

    st.markdown("<p style='font-weight: bold; margin-bottom: 5px;'>Enter username</p>", unsafe_allow_html=True)
    teacher_username = st.text_input(
        "Teacher Username",
        placeholder="@ashishek",
        label_visibility="collapsed",
        key="login_teacher_uname",
    )

    st.markdown(
        "<p style='font-weight: bold; margin-bottom: 5px; margin-top: 15px;'>Enter password</p>",
        unsafe_allow_html=True,
    )
    teacher_password = st.text_input(
        "Teacher Password",
        type="password",
        placeholder="Enter your password",
        label_visibility="collapsed",
        key="login_teacher_pass",
    )

    st.markdown("---")

    st.markdown('<span class="teacher-auth-actions-marker"></span>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login - Enter", width="stretch", key="login_teacher_btn", type="primary"):
            if login_teacher(teacher_username, teacher_password):
                teacher_data = st.session_state["teacher_info"]
                st.session_state["teacher_flash"] = f"Welcome back, {teacher_data['name']}!"
                st.rerun()

            st.error("Invalid username or password combo")

    with col2:
        if st.button("Register instead", width="stretch", key="switch_to_reg_btn"):
            st.session_state["teacher_mode"] = "register"
            st.rerun()


def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."
    return True, ""


def register_teacher_logic(name, username, password, confirm_password):
    if not username or not name or not password or not confirm_password:
        return False, "All fields are required!"

    teacher_db = get_teacher_db()
    if teacher_db.check_teacher_exists(username):
        return False, "Username already taken"
    if password != confirm_password:
        return False, "Passwords don't match"

    is_valid, error_msg = validate_password(password)
    if not is_valid:
        return False, error_msg

    try:
        teacher_db.create_teacher(username, password, name)
        return True, "Successfully Created! Login Now"
    except Exception as e:
        return False, f"Unexpected Error: {str(e)}"


def render_teacher_register():
    apply_custom_button_styles()

    st.markdown("<p style='font-weight: bold; margin-bottom: 5px;'>Enter name</p>", unsafe_allow_html=True)
    teacher_name = st.text_input(
        "Teacher Name",
        placeholder="Enter your name",
        label_visibility="collapsed",
        key="reg_teacher_name",
    )

    st.markdown(
        "<p style='font-weight: bold; margin-bottom: 5px; margin-top: 15px;'>Enter username</p>",
        unsafe_allow_html=True,
    )
    teacher_username = st.text_input(
        "Teacher Username",
        placeholder="Choose a username",
        label_visibility="collapsed",
        key="reg_teacher_uname",
    )

    st.markdown(
        "<p style='font-weight: bold; margin-bottom: 5px; margin-top: 15px;'>Enter password</p>",
        unsafe_allow_html=True,
    )
    st.caption("Must be 8+ chars, include Uppercase, Lowercase, Number, and Special Char (!@#$%^&*)")
    teacher_password = st.text_input(
        "Teacher Password",
        type="password",
        placeholder="Choose a strong password",
        label_visibility="collapsed",
        key="reg_teacher_pass",
    )

    st.markdown(
        "<p style='font-weight: bold; margin-bottom: 5px; margin-top: 15px;'>Confirm Password</p>",
        unsafe_allow_html=True,
    )
    teacher_confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Confirm your password",
        label_visibility="collapsed",
        key="reg_teacher_confirm",
    )

    st.markdown("---")

    st.markdown('<span class="teacher-auth-actions-marker"></span>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Register", width="stretch", key="reg_teacher_btn", type="primary"):
            success, message = register_teacher_logic(
                teacher_name,
                teacher_username,
                teacher_password,
                teacher_confirm_password,
            )
            if success:
                st.session_state["teacher_flash"] = message
                st.session_state["teacher_mode"] = "login"
                st.rerun()

            st.error(message)

    with col2:
        if st.button("Login instead", width="stretch", key="switch_to_login_btn"):
            st.session_state["teacher_mode"] = "login"
            st.rerun()


def login_teacher(username, password):
    if not username or not password:
        return False

    teacher_data = get_teacher_db().teacher_login(username, password)
    if not teacher_data:
        return False

    st.session_state["teacher_logged_in"] = True
    st.session_state["teacher_info"] = teacher_data
    st.session_state["user_role"] = "teacher"
    return True


def logout_teacher():
    st.session_state["teacher_logged_in"] = False
    st.session_state["login_type"] = None
    clear_teacher_transient_state(clear_attendance_images=True)

    for key in ("teacher_info", "teacher_mode", "current_teacher_tab", "current_attendance"):
        if key in st.session_state:
            del st.session_state[key]


def style_teacher_dashboard_controls():
    st.markdown(
        """
        <style>
        div[data-testid="stButton"] {
            width: fit-content !important;
            max-width: 100% !important;
        }

        div[data-testid="stButton"] > button {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 0.55rem !important;
            width: fit-content !important;
            min-width: min(12.5rem, 100%) !important;
            max-width: 100% !important;
            min-height: 50px !important;
            height: auto !important;
            border: none !important;
            border-radius: 799px !important;
            background: #df2c8a !important;
            color: #ffffff !important;
            padding: 0.7rem 2rem 0.7rem 1.15rem !important;
            font-weight: 800 !important;
            line-height: 1 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            box-shadow: none !important;
            
        }

        div[data-testid="stButton"] > button p,
        div[data-testid="stButton"] > button span,
        div[data-testid="stButton"] > button svg {
            color: #ffffff !important;
            fill: currentColor !important;
            font-weight: 800 !important;
            line-height: 1 !important;
            margin: 0 !important;
            white-space: nowrap !important;
            text-align: center !important;
        }

        div[data-testid="stButton"] > button:hover {
            transform: translateY(-1px) !important;
            background: #c91f79 !important;
        }

        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stButton"]) {
            transform: none !important;
        }

        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stButton"]) div[data-testid="stColumn"] {
            background: transparent !important;
            padding: 0 !important;
            border-radius: 0 !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.teacher-tab-row-marker) {
            align-items: center !important;
            gap: 1.25rem !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.teacher-tab-row-marker) div[data-testid="stColumn"]:nth-of-type(1) div[data-testid="stButton"],
        div[data-testid="stHorizontalBlock"]:has(.teacher-tab-row-marker) div[data-testid="stColumn"]:nth-of-type(1) button,
        div[data-testid="stHorizontalBlock"]:has(.teacher-tab-row-marker) div[data-testid="stColumn"]:nth-of-type(3) div[data-testid="stButton"],
        div[data-testid="stHorizontalBlock"]:has(.teacher-tab-row-marker) div[data-testid="stColumn"]:nth-of-type(3) button {
            width: 100% !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_teacher_dashboard():
    style_teacher_dashboard_controls()
    teacher_data = st.session_state.get("teacher_info", {})
    teacher_name = teacher_data.get("name", "Teacher")

    st.markdown(
        f"""
        <div style='padding: 1.5rem 0;'>
            <h1 style='color: #5865f2; margin-bottom: 0.25rem;'>Welcome, {teacher_name}!</h1>
            <p style='font-size: 1.1rem; color: #555;'>Teacher Portal</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "current_attendance" in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"

    st.markdown('<span class="teacher-tab-row-marker"></span>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.columns([1, 1, 1.25], gap="large")
    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == "take_attendance" else "secondary"
        if st.button("Take Attendance", type=type1, icon=":material/how_to_reg:", width="stretch"):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == "manage_subjects" else "secondary"
        if st.button("Manage Subjects", type=type2, icon=":material/book_ribbon:"):
            st.session_state.current_teacher_tab = "manage_subjects"
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == "attendance_records" else "secondary"
        if st.button("Attendance Records", type=type3, icon=":material/cards_stack:", width="stretch"):
            st.session_state.current_teacher_tab = "attendance_records"
            st.rerun()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()


def teacher_tab_take_attendance():
    teacher_id = st.session_state["teacher_info"]["teacher_id"]
    st.header("Take AI Attendance")

    if "attendance_images" not in st.session_state:
        st.session_state.attendance_images = []

    subjects = cached_teacher_subjects(teacher_id)

    if not subjects:
        st.warning("you have not created any subject yet. Please create a subject to  begin")
        return

    subject_options = {f"{s['name']} - {s['subject_code']}": s["subject_id"] for s in subjects}

    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")

    with col1:
        selected_subject_label = st.selectbox("select subject", options=list(subject_options.keys()))

    with col2:
        if st.button("Add Photos", type="primary", icon=":material/photo_prints:", width="stretch"):
            add_photos_dialog = get_add_photos_dialog()
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.header("Captured Photos")
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img, width="stretch", caption=f"Photo {idx + 1}")

        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("Clear all photos", width="stretch", type="tertiary", icon=":material/delete:"):
                st.session_state.attendance_images = []
                st.rerun()

        with c2:
            if st.button("Run Face Analysis", width="stretch", type="tertiary", icon=":material/search:"):
                with st.spinner("Deep Scanning classroom photos.."):
                    import numpy as np
                    import pandas as pd

                    attendance_result_dialog = get_attendance_result_dialog()
                    predict_attendance = get_face_attendance_predictor()
                    load_subject_students = get_subject_students_loader()
                    enrolled_students = load_subject_students(selected_subject_id)
                    all_detected_id = {}

                    if enrolled_students:
                        for idx, img in enumerate(st.session_state.attendance_images):
                            img_np = np.array(img.convert("RGB"))
                            detected, _, _ = predict_attendance(img_np, enrolled_students)

                            if detected:
                                for sid in detected.keys():
                                    student_id = int(sid)
                                    all_detected_id.setdefault(student_id, []).append(f"Photo {idx + 1}")

                if not enrolled_students:
                    st.warning("No students enrolled in this subject yet!")
                else:
                    results, attendance_to_log = [], []
                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for node in enrolled_students:
                        student = node["students"]
                        sources = all_detected_id.get(int(student["student_id"]), [])
                        is_present = len(sources) > 0

                        results.append(
                            {
                                "Name": student["name"],
                                "ID": student["student_id"],
                                "Source": ",".join(sources) if is_present else "-",
                                "Status": "Present" if is_present else "Absent",
                            }
                        )

                        attendance_to_log.append(
                            {
                                "student_id": student["student_id"],
                                "subject_id": selected_subject_id,
                                "timestamp": current_timestamp,
                                "is_present": is_present,
                            }
                        )

                    attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

        with c3:
            if st.button("Use Voice Attendance", type="primary", width="stretch", icon=":material/mic:"):
                voice_attendance_dialog = get_voice_attendance_dialog()
                voice_attendance_dialog(selected_subject_id)
    else:
        c1, c2, c3 = st.columns(3)

        with c1:
            st.button("Clear all photos", width="stretch", type="tertiary", icon=":material/delete:", disabled=True)

        with c2:
            st.button("Run Face Analysis", width="stretch", type="tertiary", icon=":material/search:", disabled=True)

        with c3:
            if st.button("Use Voice Attendance", type="primary", width="stretch", icon=":material/mic:"):
                voice_attendance_dialog = get_voice_attendance_dialog()
                voice_attendance_dialog(selected_subject_id)


def style_manage_subjects():
    st.markdown(
        """
        <style>
        .manage-subjects-shell {
            border-top: 1px solid rgba(31, 41, 55, 0.14);
            margin-top: 1.25rem;
            padding-top: 1.4rem;
        }

        .manage-subjects-title {
            color: #292a3a !important;
            font-size: 2.25rem !important;
            font-weight: 900 !important;
            line-height: 0.82 !important;
            letter-spacing: 0 !important;
            margin: 0 0 0.55rem 0 !important;
        }

        .subject-card {
            background: #ffffff;
            border: 1.5px solid #3f3f46;
            border-radius: 18px;
            padding: 1.45rem 1.55rem 1.25rem;
            margin: 0.75rem 0 0.7rem;
            box-shadow: none;
        }

        .subject-card h3 {
            color: #2f3142 !important;
            font-size: 1.22rem !important;
            font-weight: 800 !important;
            margin: 0 0 1.2rem !important;
            line-height: 1.25 !important;
        }

        .subject-meta {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.45rem;
            color: #5e6377;
            font-size: 0.95rem;
            margin-bottom: 0.85rem;
        }

        .subject-meta strong {
            color: #5865f2;
            font-weight: 800;
        }

        .subject-divider {
            color: #9ca3af;
        }

        .subject-stats {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.55rem;
        }

        .subject-stat-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.2rem;
            border-radius: 9px;
            background: #fff4f8;
            color: #3f3f46;
            padding: 0.28rem 0.48rem;
            font-size: 0.74rem;
            font-weight: 650;
        }

        .subject-stat-chip strong {
            color: #27272a;
            font-weight: 850;
        }

        .manage-empty {
            background: #ffffff;
            border: 1.5px dashed #a4a7c5;
            border-radius: 18px;
            padding: 1.4rem;
            color: #4b5563;
            font-weight: 700;
        }

        div[data-testid="stHorizontalBlock"]:has(.manage-subjects-title) {
            transform: none !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.manage-subjects-title) div[data-testid="stColumn"] {
            background: transparent !important;
            padding: 0 !important;
            border-radius: 0 !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def teacher_tab_manage_subjects():
    style_manage_subjects()
    teacher_id = st.session_state["teacher_info"]["teacher_id"]

    st.markdown('<div class="manage-subjects-shell"></div>', unsafe_allow_html=True)
    title_col, action_col = st.columns([1.2, 1], vertical_alignment="center")
    with title_col:
        st.markdown('<h2 class="manage-subjects-title">Manage<br>Subjects</h2>', unsafe_allow_html=True)

    with action_col:
        if st.button("Create New Subject", type="primary"):
            create_subject_dialog = get_create_subject_dialog()
            create_subject_dialog(teacher_id)

    subjects = cached_teacher_subjects(teacher_id)
    if not subjects:
        st.markdown('<div class="manage-empty">NO SUBJECT FOUND ! CREATE A NEW SUBJECT</div>', unsafe_allow_html=True)
        return

    for sub in subjects:
        subject_name = sub["name"]
        subject_code = sub["subject_code"]
        stats = [
            ("Students", "Students", sub["total_students"]),
            ("Classes", "Classes", sub["total_classes"]),
        ]

        def share_btn(subject_name=subject_name, share_code=subject_code):
            if st.button(
                "Share Code",
                key=f"share_{share_code}",
                type="primary",
                icon=":material/share:",
            ):
                share_subject_dialog = get_share_subject_dialog()
                share_subject_dialog(subject_name, share_code)
            st.space()

        subject_card(
            name=subject_name,
            subject_code=subject_code,
            section=sub["section"],
            stats=stats,
            fotter_callback=share_btn,
        )


def teacher_tab_attendance_records():
    import pandas as pd

    st.header("Attendance Records")

    teacher_id = st.session_state.get("teacher_info", {}).get("teacher_id")
    if not teacher_id:
        st.error("Teacher session not found. Please log in again.")
        return

    records = cached_teacher_attendance(teacher_id)
    if not records:
        st.info("No attendance records found yet.")
        return

    rows = []
    for record in records:
        subject = record.get("subjects") or {}
        timestamp = record.get("timestamp")
        timestamp_text = str(timestamp) if timestamp else ""
        session_key = timestamp_text.split(".")[0] if timestamp_text else "Unknown"
        normalized_timestamp = timestamp_text.replace("Z", "+00:00")

        parsed_time = None
        if timestamp_text:
            try:
                parsed_time = datetime.fromisoformat(normalized_timestamp)
            except ValueError:
                for fmt in ("%y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
                    try:
                        parsed_time = datetime.strptime(session_key, fmt)
                        break
                    except ValueError:
                        continue

        rows.append(
            {
                "Session": session_key,
                "Time": parsed_time.strftime("%Y-%m-%d %I:%M %p") if parsed_time else session_key,
                "Subject": subject.get("name", "Unknown"),
                "Subject Code": subject.get("subject_code", "N/A"),
                "Present": bool(record.get("is_present", False)),
            }
        )

    df = pd.DataFrame(rows)
    summary = (
        df.groupby(["Session", "Time", "Subject", "Subject Code"], as_index=False)
        .agg(
            Present_Count=("Present", "sum"),
            Total_Count=("Present", "count"),
        )
    )

    summary["Attendance Stats"] = (
        summary["Present_Count"].astype(int).astype(str)
        + "/"
        + summary["Total_Count"].astype(int).astype(str)
        + " students present"
    )

    display_df = (
        summary.sort_values(by="Session", ascending=False)
        [["Time", "Subject", "Subject Code", "Attendance Stats"]]
    )

    st.dataframe(display_df, width="stretch", hide_index=True)


def teacher_screen():
    style_background_dashboard()
    style_base_layout()
    style_teacher_auth_layout()

    flash_message = st.session_state.pop("teacher_flash", None)
    if flash_message:
        st.success(flash_message)

    if st.session_state.get("teacher_logged_in") and st.session_state.get("teacher_info"):
        header_col, logout_col = st.columns([4, 1], vertical_alignment="center")
        with header_col:
            header_dashboard()
        with logout_col:
            if st.button("Logout", key="teacher_logout_btn", type="secondary", width="stretch"):
                logout_teacher()
                st.rerun()

        render_teacher_dashboard()
        fotter_dashboard()
        return

    header_dashboard()

    _, col2 = st.columns([4, 1])
    with col2:
        st.markdown('<span class="teacher-back-marker"></span>', unsafe_allow_html=True)
        if st.button("Back To Home", type="secondary", width="stretch", key="teacher_back_btn"):
            if "teacher_mode" in st.session_state:
                del st.session_state["teacher_mode"]
            navigate_to(None)

    if "teacher_mode" not in st.session_state:
        st.session_state["teacher_mode"] = "login"

    _, auth_col, _ = st.columns([0.18, 0.64, 0.18])
    with auth_col:
        st.markdown('<span class="teacher-auth-marker"></span>', unsafe_allow_html=True)
        if st.session_state["teacher_mode"] == "login":
            st.header("Login Using Password")
            render_teacher_login()
        else:
            st.header("Register Your Teacher Profile")
            render_teacher_register()

    fotter_dashboard()
