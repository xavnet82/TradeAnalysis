
import streamlit as st

def render_score_card(title, score, justificaciones, color):
    with st.container():
        st.markdown(
            f"""
            <div style="border-radius:10px; padding:15px; background-color:{color};">
                <h4>{title}</h4>
                <p><b>Score:</b> <span style="font-size:24px;">{score}/100</span></p>
            </div>
            """,
            unsafe_allow_html=True
        )
        for j in justificaciones:
            st.caption(j)
