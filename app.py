import streamlit as st

from src.database.db import DatabaseConnectionError
from src.screens.home_screen import home_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen


def main() -> None:
    st.set_page_config(
        page_title="AI Attendance System",
        page_icon=":material/how_to_reg:",
        layout="wide",
    )

    login_type = st.session_state.get("login_type")
    try:
        if login_type == "student":
            student_screen()
        elif login_type == "teacher":
            teacher_screen()
        else:
            home_screen()
    except DatabaseConnectionError as exc:
        st.error(str(exc))
        st.info("Your Supabase project host must resolve before login, subjects, and attendance can load.")


if __name__ == "__main__":
    main()
