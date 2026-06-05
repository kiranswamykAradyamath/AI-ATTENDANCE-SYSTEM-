import base64
from pathlib import Path

import streamlit as st

from src.screens.components.fotter import fotter_home
from src.screens.components.header import LOGO_PATH
from src.ui.base_layout import style_background_home, style_base_layout
from src.ui.navigation import navigate_to


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STUDENT_ICON_PATH = str(PROJECT_ROOT / "assets" / "student_icon.png")
TEACHER_ICON_PATH = str(PROJECT_ROOT / "assets" / "logo_teacher.png")


@st.cache_data(show_spinner=False)
def load_image_base64(image_path: str) -> str | None:
    """Read a local image once and reuse it across Streamlit reruns."""
    path = Path(image_path)
    if not path.exists() or not path.is_file():
        return None

    return base64.b64encode(path.read_bytes()).decode()


def image_html(image_path: str, alt_text: str) -> str:
    image_b64 = load_image_base64(image_path)
    if not image_b64:
        return '<div class="role-fallback">AI</div>'

    return f'<img src="data:image/png;base64,{image_b64}" alt="{alt_text}" />'


def apply_home_layout_styles() -> None:
    """Style the landing page to match the polished role-selection mockup."""
    st.markdown(
        """
        <style>
        .stApp {
            overflow: hidden;
            background:
                radial-gradient(circle at 2% 0%, rgba(144, 155, 245, 0.30) 0 11rem, transparent 11.2rem),
                radial-gradient(circle at 98% 40%, rgba(167, 179, 255, 0.32) 0 17rem, transparent 17.2rem),
                radial-gradient(circle at 50% 118%, rgba(84, 113, 246, 0.52) 0 29rem, transparent 29.3rem),
                linear-gradient(135deg, #eef0ff 0%, #f8fbff 42%, #dfe6ff 100%) !important;
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: auto -5vw -10vh -5vw;
            height: 34vh;
            pointer-events: none;
            background:
                repeating-radial-gradient(ellipse at center, rgba(255, 255, 255, 0.45) 0 1px, transparent 2px 15px);
            opacity: 0.58;
            transform: rotate(-7deg);
        }

        .stApp::after {
            content: "";
            position: fixed;
            top: 3.8rem;
            right: 2.8rem;
            width: 9rem;
            height: 9rem;
            pointer-events: none;
            background-image: radial-gradient(rgba(255, 255, 255, 0.78) 1.4px, transparent 1.4px);
            background-size: 18px 18px;
            opacity: 0.78;
        }

        .block-container {
            max-width: 1040px;
            padding-top: 2.1rem !important;
            padding-bottom: 5.4rem !important;
            position: relative;
            z-index: 1;
        }

        .home-hero {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin: 0 auto 0.65rem;
        }

        .home-title {
            color: #090d42 !important;
            font-family: 'Google Sans', sans-serif !important;
            font-size: clamp(3.3rem, 7vw, 5.05rem) !important;
            font-weight: 950 !important;
            line-height: 0.98 !important;
            letter-spacing: 0 !important;
            margin: 0 !important;
            text-align: center !important;
            text-shadow: 0 12px 32px rgba(77, 82, 190, 0.13);
        }

        .home-title .ai-word {
            background: linear-gradient(135deg, #6457ff 0%, #322fdb 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }

        .home-tagline {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            color: #697194;
            font-size: clamp(1rem, 2vw, 1.18rem);
            font-weight: 800;
            margin: 1rem 0 1.55rem;
            white-space: nowrap;
        }

        .home-tagline::before,
        .home-tagline::after {
            content: "";
            display: block;
            width: clamp(3.2rem, 9vw, 6.5rem);
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.35), transparent);
        }

        .home-logo-orbit {
            display: flex;
            align-items: center;
            justify-content: center;
            width: clamp(9rem, 14vw, 10.8rem);
            height: clamp(9rem, 14vw, 10.8rem);
            border-radius: 50%;
            background:
                radial-gradient(circle, rgba(255, 255, 255, 0.95) 0 58%, rgba(255, 255, 255, 0.44) 59% 70%, transparent 71%),
                conic-gradient(from 210deg, rgba(98, 87, 255, 0.7), rgba(255, 255, 255, 0.9), rgba(98, 87, 255, 0.45), rgba(255, 255, 255, 0.9));
            box-shadow:
                0 22px 46px rgba(79, 86, 205, 0.22),
                inset 0 0 0 2px rgba(255, 255, 255, 0.72);
            margin-bottom: -0.3rem;
        }

        .home-logo-inner {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 72%;
            height: 72%;
            border-radius: 50%;
            background: #ffffff;
            box-shadow: 0 12px 28px rgba(68, 74, 188, 0.14);
            padding: 1.15rem;
        }

        .home-logo-inner img {
            display: block;
            width: 100%;
            height: 100%;
            object-fit: contain;
        }

        /* Override the older base layout offsets and card rules only for this page. */
        .stApp div[data-testid="stHorizontalBlock"] {
            transform: none !important;
            align-items: stretch !important;
            justify-content: center !important;
            gap: clamp(2rem, 7vw, 6.4rem) !important;
            margin-top: 0.2rem !important;
        }

        .stApp div[data-testid="stColumn"] {
            position: relative !important;
            overflow: hidden !important;
            background:
                linear-gradient(145deg, rgba(255, 255, 255, 0.86), rgba(250, 253, 255, 0.72)) !important;
            border: 2px solid rgba(255, 255, 255, 0.92) !important;
            border-radius: 34px !important;
            box-shadow:
                0 22px 52px rgba(77, 92, 194, 0.20),
                inset 0 0 0 1px rgba(255, 255, 255, 0.70) !important;
            min-height: clamp(26rem, 48vw, 31.4rem) !important;
            padding: clamp(2.4rem, 4vw, 3.15rem) clamp(1.7rem, 3vw, 2.35rem) 2rem !important;
            backdrop-filter: blur(18px);
        }

        .stApp div[data-testid="stColumn"]::before {
            content: "";
            position: absolute;
            top: -3.6rem;
            width: 9rem;
            height: 9rem;
            border-radius: 50%;
            opacity: 0.28;
        }

        .stApp div[data-testid="stColumn"]:nth-of-type(1)::before {
            left: -3.9rem;
            background: #7465ff;
        }

        .stApp div[data-testid="stColumn"]:nth-of-type(2)::before {
            right: -3.6rem;
            background: #32bd7b;
        }

        .stApp div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {
            min-height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem;
            position: relative;
            z-index: 1;
        }

        .role-art {
            display: flex;
            align-items: center;
            justify-content: center;
            width: clamp(8.7rem, 17vw, 12rem);
            height: clamp(8.7rem, 17vw, 12rem);
            border-radius: 50%;
            margin: 0 auto 0.55rem;
            background: rgba(255, 255, 255, 0.76);
            box-shadow:
                0 16px 30px rgba(70, 74, 190, 0.16),
                inset 0 0 0 8px rgba(255, 255, 255, 0.8);
        }

        .role-art img {
            display: block;
            width: 76%;
            height: 76%;
            object-fit: contain;
            border-radius: 50%;
        }

        .role-fallback {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 76%;
            height: 76%;
            border-radius: 50%;
            color: #ffffff;
            font-size: 2.8rem;
            font-weight: 950;
            background: linear-gradient(135deg, #635bff, #1b277d);
        }

        .stApp div[data-testid="stColumn"]:nth-of-type(1) .role-art {
            border: 5px solid rgba(99, 91, 255, 0.55);
        }

        .stApp div[data-testid="stColumn"]:nth-of-type(2) .role-art {
            border: 5px solid rgba(18, 170, 103, 0.55);
            box-shadow:
                0 16px 30px rgba(14, 150, 91, 0.16),
                inset 0 0 0 8px rgba(255, 255, 255, 0.8);
        }

        .role-copy {
            text-align: center;
            margin: 0 auto;
        }

        .role-kicker {
            color: #0e123f !important;
            font-size: clamp(1.18rem, 2vw, 1.35rem) !important;
            font-weight: 900 !important;
            line-height: 1 !important;
            margin: 0 0 0.2rem !important;
            text-align: center !important;
        }

        .role-name {
            font-family: 'Google Sans', sans-serif !important;
            font-size: clamp(2.05rem, 4.4vw, 2.85rem) !important;
            font-weight: 950 !important;
            line-height: 1 !important;
            letter-spacing: 0 !important;
            margin: 0 !important;
            text-align: center !important;
        }

        .role-name.student {
            color: #5147f3 !important;
        }

        .role-name.teacher {
            color: #09965e !important;
        }

        .role-divider {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.45rem;
            margin: 1.25rem auto 1.05rem;
        }

        .role-divider::before,
        .role-divider::after {
            content: "";
            width: 2.6rem;
            height: 2px;
            background: currentColor;
            opacity: 0.26;
        }

        .role-divider span {
            display: block;
            width: 0.55rem;
            height: 0.55rem;
            border-radius: 50%;
            background: currentColor;
        }

        .role-divider.student {
            color: #5147f3;
        }

        .role-divider.teacher {
            color: #09965e;
        }

        .role-description {
            color: #4d5776 !important;
            font-size: clamp(1rem, 1.7vw, 1.12rem) !important;
            font-weight: 650 !important;
            line-height: 1.38 !important;
            margin: 0 auto 1rem !important;
            max-width: 16rem;
            text-align: center !important;
        }

        .stApp div[data-testid="stButton"] {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
            margin-top: auto !important;
        }

        .stApp div[data-testid="stButton"] > button {
            width: min(100%, 18rem) !important;
            min-height: 3.75rem !important;
            border: none !important;
            border-radius: 15px !important;
            color: #ffffff !important;
            font-size: 1.12rem !important;
            font-weight: 900 !important;
            box-shadow: 0 14px 26px rgba(53, 63, 177, 0.26) !important;
            margin: 0 auto !important;
            position: static !important;
        }

        .stApp div[data-testid="stButton"] > button p,
        .stApp div[data-testid="stButton"] > button span {
            color: #ffffff !important;
            font-weight: 900 !important;
        }

        .stApp div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]:nth-of-type(1) button {
            background: linear-gradient(135deg, #695bff 0%, #4537df 100%) !important;
        }

        .stApp div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]:nth-of-type(2) button {
            background: linear-gradient(135deg, #18bd74 0%, #078c55 100%) !important;
            box-shadow: 0 14px 26px rgba(7, 140, 85, 0.28) !important;
        }

        .home-footer {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            position: fixed;
            left: 0;
            right: 0;
            bottom: 1.15rem;
            z-index: 20;
            margin: 0 auto;
            color: #12173d;
            font-size: 1.05rem;
            font-weight: 800;
            pointer-events: none;
        }

        .creator-pill {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.7rem;
            min-height: 2.65rem;
            padding: 0 1.55rem;
            border-radius: 999px;
            color: #141943;
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(255, 255, 255, 0.95);
            box-shadow: 0 12px 28px rgba(70, 80, 190, 0.13);
            font-size: 0.98rem;
            font-weight: 950;
            letter-spacing: 0.26rem;
            pointer-events: auto;
        }

        .creator-logo {
            display: block;
            width: 2.1rem;
            height: 2.1rem;
            border-radius: 50%;
            object-fit: contain;
            background: #ffffff;
        }

        @media (max-width: 760px) {
            .block-container {
                padding-top: 1.4rem !important;
                padding-bottom: 6.2rem !important;
            }

            .home-tagline {
                flex-wrap: wrap;
                gap: 0.7rem;
                white-space: normal;
            }

            .stApp div[data-testid="stColumn"] {
                min-height: 25rem !important;
                border-radius: 28px !important;
            }

            .home-footer {
                gap: 0.65rem;
                flex-wrap: wrap;
                bottom: 0.75rem;
                font-size: 0.95rem;
            }

            .creator-pill {
                min-height: 2.35rem;
                padding: 0 1rem;
                font-size: 0.82rem;
                letter-spacing: 0.16rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_home_header() -> None:
    logo_html = image_html(LOGO_PATH, "AI Attendance System logo")

    st.markdown(
        f"""
        <section class="home-hero">
            <h1 class="home-title"><span class="ai-word">AI</span> Attendance System</h1>
            <div class="home-tagline">Smart <span>&bull;</span> Accurate <span>&bull;</span> Automated</div>
            <div class="home-logo-orbit">
                <div class="home-logo-inner">{logo_html}</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_role_content(role: str, description: str, image_path: str, accent_class: str) -> None:
    st.markdown(
        f"""
        <div class="role-art">{image_html(image_path, role + " illustration")}</div>
        <div class="role-copy">
            <p class="role-kicker">I'm a</p>
            <h2 class="role-name {accent_class}">{role}</h2>
            <div class="role-divider {accent_class}"><span></span></div>
            <p class="role-description">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_portal_button(label: str, login_type: str, *, primary: bool = False) -> None:
    if st.button(
        label,
        width="stretch",
        type="primary" if primary else "secondary",
        icon=":material/arrow_outward:",
        icon_position="right",
        key=f"{login_type}_portal_button",
    ):
        navigate_to(login_type)


def home_screen() -> None:
    style_background_home()
    style_base_layout()
    apply_home_layout_styles()

    render_home_header()

    student_col, teacher_col = st.columns(2, gap="large")

    with student_col:
        render_role_content(
            "Student",
            "Mark your attendance and track your learning.",
            STUDENT_ICON_PATH,
            "student",
        )
        render_portal_button("Student Portal", "student")

    with teacher_col:
        render_role_content(
            "Teacher",
            "Manage classes, attendance and students efficiently.",
            TEACHER_ICON_PATH,
            "teacher",
        )
        render_portal_button("Teacher Portal", "teacher", primary=True)

    fotter_home()
