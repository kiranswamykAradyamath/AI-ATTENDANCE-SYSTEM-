import hashlib

import streamlit as st

from src.ui.navigation import clear_teacher_transient_state

from PIL import Image


def _file_hash(file_obj):
    return hashlib.sha256(file_obj.getvalue()).hexdigest()


@st.dialog("capture or upload photos")
def dialog_add_photo():
    st.write("Add Classroom photos to scan for attendance")

    if 'photo_tab' not in st.session_state:
        st.session_state.photo_tab = 'camera'

    t1, t2 = st.columns(2)

    with t1:
        type_camera = "primary" if st.session_state.photo_tab == 'camera' else "tertiary"
        if st.button("Camera", type=type_camera, width="stretch"):
            st.session_state.photo_tab = 'camera'
            
    with t2:
        type_upload = "primary" if st.session_state.photo_tab == 'upload' else "tertiary"
        if st.button("Upload photos", type=type_upload, width="stretch"):
            st.session_state.photo_tab = 'upload'
        

    if st.session_state.photo_tab == 'camera':
        cam_photo = st.camera_input("Take a photo", key = 'dialog_cam')
        if cam_photo:
            photo_hash = _file_hash(cam_photo)
            if st.session_state.get("dialog_cam_hash") != photo_hash:
                st.session_state.attendance_images.append(Image.open(cam_photo).copy())
                st.session_state.dialog_cam_hash = photo_hash
                st.toast('Photo Captutred!')
                st.rerun()

    if st.session_state.photo_tab == 'upload':
        uploaded_files = st.file_uploader("Upload photos", type=['jpg','png', 'jpeg'],accept_multiple_files=True, key = 'dialog_upload')

        if uploaded_files:
            seen_hashes = set(st.session_state.get("dialog_upload_hashes", []))
            new_hashes = []
            for f in uploaded_files :
                upload_hash = _file_hash(f)
                if upload_hash not in seen_hashes:
                    st.session_state.attendance_images.append(Image.open(f).copy())
                    seen_hashes.add(upload_hash)
                    new_hashes.append(upload_hash)
            if new_hashes:
                st.session_state.dialog_upload_hashes = list(seen_hashes)
                st.rerun()

    st.divider()
    if st.button('Done', type="primary", width="stretch"):
        clear_teacher_transient_state(clear_attendance_images=False)
        st.rerun()


        
        
        
        
        
        
