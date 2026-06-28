from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
ASSETS_DIR = PROJECT_ROOT / "assets"
LOCAL_WEIGHTS = PROJECT_ROOT / ".deepface" / "weights" / "vgg_face_weights.h5"


def configure_imports() -> None:
    """Make project modules importable when Streamlit runs app.py directly."""
    project_path = str(PROJECT_ROOT)
    if project_path not in sys.path:
        sys.path.insert(0, project_path)


def configure_model_home() -> None:
    """
    Set DEEPFACE_HOME before any DeepFace import happens.

    Local development can use a pre-downloaded project-local model. Streamlit
    Cloud uses the user home directory and downloads weights there at runtime.
    """
    if LOCAL_WEIGHTS.exists() and LOCAL_WEIGHTS.stat().st_size > 100_000_000:
        os.environ["DEEPFACE_HOME"] = str(PROJECT_ROOT)
    else:
        os.environ.setdefault("DEEPFACE_HOME", str(Path.home()))


def validate_deployment_files() -> bool:
    """
    Confirm the repository files required by app.py are present.

    Streamlit Cloud should deploy this whole repo with app.py as the entrypoint.
    Deploying only the single app.py file will not include screens, pipelines,
    database helpers, or visual assets.
    """
    missing_paths = [
        path
        for path in (
            SRC_DIR,
            ASSETS_DIR,
            PROJECT_ROOT / "requirements.txt",
            SRC_DIR / "screens",
            SRC_DIR / "pipelines",
            SRC_DIR / "database",
        )
        if not path.exists()
    ]

    if not missing_paths:
        return True

    st.error(
        "Deployment is missing required project files. Deploy the full GitHub "
        "repository and set Streamlit's main file path to app.py."
    )
    with st.expander("Missing files"):
        for path in missing_paths:
            st.code(str(path.relative_to(PROJECT_ROOT)))
    return False


configure_imports()
configure_model_home()

from src.screens.components.dialog_auto_enroll import auto_enroll_dialog
from src.screens.home_screen import home_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen
from src.utils.model_loader import ensure_models_ready


def route_app() -> None:
    if "login_type" not in st.session_state:
        st.session_state["login_type"] = None

    match st.session_state["login_type"]:
        case "teacher":
            teacher_screen()
        case "student":
            student_screen()
        case _:
            home_screen()


def handle_join_link() -> None:
    join_code = st.query_params.get("join-code") or st.query_params.get("subject")
    if not join_code:
        return

    if st.session_state.login_type != "student":
        st.session_state.login_type = "student"
        st.rerun()

    if (
        st.session_state.get("is_logged_in")
        and st.session_state.get("user_role") == "student"
    ):
        auto_enroll_dialog(join_code)


def main() -> None:
    st.set_page_config(
        page_title="AI Attendance System",
        page_icon=":material/how_to_reg:",
        layout="wide",
    )

    if not validate_deployment_files():
        st.stop()

    if not ensure_models_ready():
        st.stop()

    route_app()
    handle_join_link()


if __name__ == "__main__":
    main()
