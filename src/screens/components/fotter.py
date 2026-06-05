import base64
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FOOTER_LOGO_PATH = str(PROJECT_ROOT / "assets" / "footer_logo.png")
FOOTER_LOGO_ZOOM = 1.35


@st.cache_data(show_spinner=False)
def _logo_data_uri(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        return ""
    encoded = base64.b64encode(file_path.read_bytes()).decode()
    return f"data:image/png;base64,{encoded}"


def render_footer():
    img_src = _logo_data_uri(FOOTER_LOGO_PATH)
    creator_mark = (
        f'<img class="creator-footer-img" src="{img_src}" alt="KIRAN_SWAMY" />'
        if img_src
        else '<span class="creator-footer-name">KIRAN_SWAMY</span>'
    )

    st.markdown(
        f"""
        <style>
        .creator-footer {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.85rem;
            width: 100%;
            margin: 1.5rem auto 0.7rem;
            color: #1a1a1a;
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            font-size: 1.3rem;
            font-weight: 600;
            line-height: 1;
        }}

        .creator-footer-pill {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 7.7rem;
            height: 2.45rem;
            padding: 0;
            overflow: hidden;
            background: #ffffff;
            border: 1px solid rgba(60, 64, 90, 0.16);
            border-radius: 999px;
            box-shadow: 0 8px 22px rgba(79, 86, 205, 0.12);
        }}

        .creator-footer-img {{
            display: block;
            width: 8.9rem;
            height: 2.85rem;
            max-width: none;
            object-fit: cover;
            object-position: center;
            padding: 0;
            background: transparent;
            border: none;
            border-radius: 0;
            mix-blend-mode: normal;
            transform: scale({FOOTER_LOGO_ZOOM});
            transform-origin: center;
            filter:
                contrast(1.18)
                saturate(1.05);
            transition: all 0.3s ease;
        }}

        .creator-footer-name {{
            color: #111111;
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: 0.12rem;
            line-height: 1;
        }}
        </style>

        <div class="creator-footer" role="contentinfo">
            <span>Created by</span>
            <span class="creator-footer-pill">{creator_mark}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def fotter_home():
    render_footer()


def fotter_dashboard():
    render_footer()
