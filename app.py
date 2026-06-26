import os
import streamlit as st
from pathlib import Path


# ---------------------------------------------------------------------------
# DEEPFACE_HOME — set BEFORE any deepface import happens anywhere
# ---------------------------------------------------------------------------
# On local dev: if the project already has .deepface/weights/vgg_face_weights.h5,
#   point DeepFace to the project root so it finds the pre-downloaded weights.
# On Streamlit Cloud (or if no local weights exist): leave DEEPFACE_HOME
#   pointing to the user home dir (~) so DeepFace uses ~/.deepface/weights/
#   and our model_loader.py downloads there.
_PROJECT_ROOT = Path(__file__).resolve().parent
_LOCAL_WEIGHTS = _PROJECT_ROOT / ".deepface" / "weights" / "vgg_face_weights.h5"

if _LOCAL_WEIGHTS.exists() and _LOCAL_WEIGHTS.stat().st_size > 100_000_000:
    # Local dev: pre-downloaded weights exist in project folder
    os.environ["DEEPFACE_HOME"] = str(_PROJECT_ROOT)
else:
    # Streamlit Cloud / fresh machine: use default home dir
    os.environ.setdefault("DEEPFACE_HOME", str(Path.home()))


# ---------------------------------------------------------------------------
# Screen imports (AFTER env vars are set)
# ---------------------------------------------------------------------------
from src.screens.home_screen import home_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.components.dialog_auto_enroll import auto_enroll_dialog


def main() -> None:
    st.set_page_config(
        page_title="AI Attendance System",
        page_icon=":material/how_to_reg:",
        layout="wide",
    )

    # ── Ensure ML model weights are ready (runs once per server process) ──
    from src.utils.model_loader import ensure_models_ready
    ensure_models_ready()

    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()

        case 'student':
            student_screen()

        case None:
            home_screen()


    join_code = st.query_params.get('join-code') or st.query_params.get('subject')
    if join_code:
        if st.session_state.login_type != 'student':
            st.session_state.login_type = 'student'
            st.rerun()
        if st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'student':
            auto_enroll_dialog(join_code)


if __name__ == "__main__":
    main()
