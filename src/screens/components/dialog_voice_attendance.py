from datetime import datetime

import pandas as pd
import streamlit as st

from src.database.db import get_subject_students
from src.pipelines.voice_pipelines import process_bulk_audio
from src.screens.components.dialog_attendance_result import attendance_result_dialog


@st.dialog("Voice Attendance")
def voice_attendance_dialog(selected_subject_id):
    st.write("Record audio of students saying they are present. AI will recognize enrolled students by voice.")

    audio_data = st.audio_input("Record Classroom audio")

    if st.button("Analyze Audio", width="stretch", type="primary"):
        if not audio_data:
            st.warning("Please record audio first.")
            return

        with st.spinner("Processing Audio data"):
            enrolled_students = get_subject_students(selected_subject_id)

            if not enrolled_students:
                st.warning("No students enrolled in this subject yet!")
                return

            candidates_dict = {
                int(node["students"]["student_id"]): node["students"]["voice_embedding"]
                for node in enrolled_students
                if node.get("students") and node["students"].get("voice_embedding")
            }

            if not candidates_dict:
                st.error("No enrolled students have voice profiles registered.")
                return

            detected_scores = process_bulk_audio(audio_data.read(), candidates_dict)

        results, attendance_to_log = [], []
        current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        for node in enrolled_students:
            student = node.get("students")
            if not student:
                continue

            student_id = int(student["student_id"])
            score = detected_scores.get(student_id)
            is_present = score is not None

            results.append({
                "Name": student["name"],
                "ID": student_id,
                "Source": f"Voice ({score:.2f})" if is_present else "-",
                "Status": "Present" if is_present else "Absent",
            })

            attendance_to_log.append({
                "student_id": student_id,
                "subject_id": selected_subject_id,
                "timestamp": current_timestamp,
                "is_present": is_present,
            })

        attendance_result_dialog(pd.DataFrame(results), attendance_to_log)
