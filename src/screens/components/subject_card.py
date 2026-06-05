from html import escape

import streamlit as st


def subject_card(name, subject_code, section, stats=None, fotter_callback=None):
    stats = stats or []
    safe_name = escape(str(name))
    safe_subject_code = escape(str(subject_code))
    safe_section = escape(str(section))

    stat_chips = []
    for stat in stats:
        if len(stat) == 2:
            label, value = stat
            icon = label
        else:
            icon, label, value = stat

        safe_icon = escape(str(icon))
        safe_label = escape(str(label))
        icon_html = "" if safe_icon == safe_label else f'<span class="subject-stat-icon">{safe_icon}</span>'
        stat_chips.append(
            f'<span class="subject-stat-chip">{icon_html}<strong>{escape(str(value))}</strong><span>{safe_label}</span></span>'
        )

    stats_html = "".join(stat_chips)
    html = f"""
    <div class="subject-card">
        <h3>{safe_name}<span class="subject-link-icon">&#128279;</span></h3>
        <div class="subject-meta">
            <span>Code : <strong>{safe_subject_code}</strong></span>
            <span class="subject-divider">|</span>
            <span>Section : <strong>{safe_section}</strong></span>
        </div>
        <div class="subject-stats">{stats_html}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    if fotter_callback:
        fotter_callback()