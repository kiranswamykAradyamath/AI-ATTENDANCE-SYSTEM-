import base64
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOGO_PATH = str(PROJECT_ROOT / "assets" / "logo.png")


@st.cache_data(show_spinner=False)
def get_image_base64(image_path):
    path = Path(image_path)
    if not path.exists() or not path.is_file():
        return None

    with path.open("rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def logo_img_html(image_path=LOGO_PATH):
    logo_b64 = get_image_base64(image_path)
    if not logo_b64:
        return ""

    return (
        f'<img src="data:image/png;base64,{logo_b64}" '
        'style="display:block; width:70px; height:70px; object-fit:contain;" '
        'alt="AI Attendance System logo" />'
    )


def header_home():
    st.markdown(f"""
<div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin:20px 0 35px;">
    <h1 style="color:#ffffff; margin:0 0 18px; text-align:center;">AI Attendance System</h1>
    <div style="display:flex; align-items:center; justify-content:center; width:112px; height:112px; background:#ffffff; border-radius:18px; box-shadow:0 8px 20px rgba(31,41,55,0.18);">
        {logo_img_html()}
    </div>
</div>
""", unsafe_allow_html=True)


def header_dashboard():
    st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:flex-start; gap:20px; margin:18px 0 34px;">
    <div style="display:flex; align-items:center; justify-content:center; flex:0 0 auto; width:112px; height:112px; background:#ffffff; border-radius:14px; box-shadow:0 8px 20px rgba(31,41,55,0.18);">
        {logo_img_html()}
    </div>
    <h2 style="color:#5865F2 !important; margin:0 !important; text-align:left !important; font-size:34px !important; font-weight:800 !important; line-height:1.08 !important; letter-spacing:0 !important;">
        AI Attendance<br>System
    </h2>
</div>
""", unsafe_allow_html=True)
