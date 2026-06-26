import time

import streamlit as st

from src.database.db import DatabaseConnectionError, create_attendance


@st.dialog("Attendance reports")
def show_attendance_result(df, logs):
    st.write("Please review attendance before confirming.")
    st.dataframe(df, hide_index=True, width="stretch")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Discard", width="stretch"):
            st.session_state.voice_attendance_results = None
            st.session_state.attendance_images = []
            st.rerun()

    with col2:
        if st.button("Confirm & Save", width="stretch", type="primary"):
            try:
                create_attendance(logs)
                st.toast("✅ Attendance saved successfully!")
                st.session_state.attendance_images = []
                st.session_state.voice_attendance_results = None
                st.rerun()
            except DatabaseConnectionError as exc:
                st.error(f"Database error: {exc}")
            except Exception as exc:
                st.error(f"Failed to save attendance: {exc}")


def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)
