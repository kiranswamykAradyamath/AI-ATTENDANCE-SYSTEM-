import streamlit as st

import segno
import io


@st.dialog("Share Class Link")
def share_subject_dialog(subject_name, subject_code):
    app_domain = "AI ATTENDANCE SYSTEM-main.streamlit.app"
    join_url = f"{app_domain}/join?subject_code={subject_code}"

    st.header("Scan to join the Subject")

    # Generate QR code
    qr_code = segno.make(join_url)
    img_buffer = io.BytesIO()
    qr_code.save(img_buffer, kind="png", scale=10, border=1)
    img_buffer.seek(0)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### Copy Link")
        st.code(join_url, language="text")
        st.code(subject_code, language="text")
        st.info("Copy this link to share on Whatsapp or Email")

    with col2:
        st.markdown("### Scan to Join")
        st.image(
            img_buffer.getvalue(),
            width="stretch",
            caption=f"QRCode for joining {subject_name}",
        )
