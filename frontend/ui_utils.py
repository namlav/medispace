from pathlib import Path

import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parent
CSS_DIR = FRONTEND_DIR / "assets" / "css"


def load_css(*filenames: str) -> None:
    """Nạp CSS chung và CSS riêng của trang hiện tại."""
    for filename in ("main.css", *filenames):
        css_path = CSS_DIR / filename

        if not css_path.is_file():
            continue

        css_content = css_path.read_text(encoding="utf-8")

        st.markdown(
            f"<style>\n{css_content}\n</style>",
            unsafe_allow_html=True,
        )
