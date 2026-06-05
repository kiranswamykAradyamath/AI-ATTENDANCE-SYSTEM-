import streamlit as st
from src.database.db import enroll_student_to_subject, find_subject_by_code, is_student_enrolled

import time

@st.dialog("Enroll in Subject")
def enroll_dialog():

    st.write('Enter the subject code by your teacher to enroll')
    join_code = st.text_input("Subject Code", placeholder="Eg.CS101")

    if st.button("Enroll Now", type="primary", width='stretch'):
        if join_code:
            subject = find_subject_by_code(join_code)

            if subject:
                student_id = st.session_state.student_data.get('student_id')
                if is_student_enrolled(student_id, subject['subject_id']):
                    st.warning('You are already enrolled in this subject')
                else:
                    enroll_student_to_subject(student_id, subject['subject_id'])
                    st.success('Successfully enrolled!')
                    time.sleep(1)
                    st.rerun()   
            else:
                st.error('No subject found with this code')

        else:

            # Here you would typically call a function to enroll the student in the subject using the join_code
            st.warning('Please enter a subject code ')

   
