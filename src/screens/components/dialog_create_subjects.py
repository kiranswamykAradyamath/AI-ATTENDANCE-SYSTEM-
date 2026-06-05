import streamlit as st
from src.database.db import create_subject


@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):
    st.write("Enter the details of new Subject")
    subject_code = st.text_input("Subject Code", placeholder="CS101")
    name = st.text_input("Subject Name", placeholder="Introduction to Computer Science")
    section = st.text_input("Section", placeholder="A")

    if st.button("Create Subject Now", type="primary", width='stretch'):
        if not teacher_id:
            st.error("Teacher session expired. Please log in again.")
            return

        if subject_code and name and section:
            try:
                create_subject(subject_code, name, section, teacher_id)
                st.toast("Subject Created Successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating subject: {str(e)}")
        else:
            st.warning("Please fill in all the fields!")   
