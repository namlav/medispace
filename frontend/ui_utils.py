from pathlib import Path
from typing import Optional
import html
import streamlit as st
import streamlit.components.v1 as components
from backend.app.models.patient import validate_patient_name

FRONTEND_DIR = Path(__file__).resolve().parent
CSS_DIR = FRONTEND_DIR / "assets" / "css"

# =====================================================================
# SVG ICON LIBRARY (Oceanic Clinical Line Icons)
# =====================================================================
SVG_ICONS = {
    "hospital": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"/><path d="M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16"/><path d="M9 21v-4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v4"/><path d="M10 9h4"/><path d="M12 7v4"/></svg>',
    "patient": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "record": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
    "analytics": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "heart": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M3.22 12H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27"/></svg>',
    "skin": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/></svg>',
    "tooth": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C8.5 2 7 4.5 7 8c0 3 1.5 5.5 1.5 8.5 0 2.5-.5 5.5 1.5 5.5s2-3 2-5c0-.5.5-1 1-1s1 .5 1 1c0 2 0 5 2 5s1.5-3 1.5-5.5c0-3 1.5-5.5 1.5-8.5 0-3.5-1.5-6-5-6Z"/></svg>',
    "pill": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"/><path d="m8.5 8.5 7 7"/></svg>',
    "database": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>',
    "zap": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "check": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "shield": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
}


def get_icon(name: str, size: int = 20, color: str = "currentColor") -> str:
    """Trả về chuỗi SVG chuẩn."""
    tpl = SVG_ICONS.get(name, SVG_ICONS["hospital"])
    return tpl.format(size=size, color=color)


def inject_sidebar_recovery_script() -> None:
    """Khôi phục trạng thái sidebar, xoá cờ khoá ẩn trong localStorage và tự động bung menu."""
    components.html(
        """
        <script>
        (function() {
            try {
                // 1. Dọn sạch các key làm kẹt trạng thái sidebar collapsed trong localStorage
                const storages = [window.localStorage];
                try {
                    if (window.parent && window.parent.localStorage) {
                        storages.push(window.parent.localStorage);
                    }
                } catch (e) {}

                storages.forEach(s => {
                    const keysToRemove = [];
                    for (let i = 0; i < s.length; i++) {
                        const k = s.key(i);
                        if (k && (k.startsWith('stSidebarCollapsed') || k.includes('sidebarState'))) {
                            keysToRemove.push(k);
                        }
                    }
                    keysToRemove.forEach(k => s.removeItem(k));
                });

                // 2. Nếu sidebar đang bị co cụm (collapsed), tìm và kích hoạt nút mở (>>)
                setTimeout(function() {
                    try {
                        const doc = window.parent ? window.parent.document : document;
                        const expandBtn = doc.querySelector('[data-testid="stExpandSidebarButton"]')
                                       || doc.querySelector('[data-testid="stSidebarCollapsedControl"]')
                                       || doc.querySelector('[data-testid="collapsedControl"]')
                                       || doc.querySelector('button[aria-label="Open sidebar"]');
                        if (expandBtn) {
                            expandBtn.click();
                        }
                    } catch (e) {}
                }, 80);
            } catch (err) {
                console.debug("MediSpace sidebar restore helper:", err);
            }
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def load_css(*filenames: str) -> None:
    """Nạp các file CSS từ thư mục assets/css và gắn mã phục hồi Sidebar."""
    all_files = ["main.css", "workstation.css"]
    for f in filenames:
        if f not in all_files:
            all_files.append(f)

    merged_css = []
    for filename in all_files:
        css_path = CSS_DIR / filename
        if css_path.is_file():
            merged_css.append(css_path.read_text(encoding="utf-8"))

    if merged_css:
        st.markdown(
            f"<style>\n{'\n'.join(merged_css)}\n</style>",
            unsafe_allow_html=True,
        )

    # Đảm bảo sidebar luôn hiển thị và không bị kẹt ẩn bởi localStorage
    inject_sidebar_recovery_script()


def format_number(val: Optional[int | float | str]) -> str:
    """Định dạng số theo chuẩn phân tách hàng nghìn y tế."""
    if val is None:
        return "—"
    try:
        return f"{int(val):,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(val)


def render_sidebar_branding() -> None:
    """Hiển thị Khung nhận diện thương hiệu MediSpace trên Sidebar."""
    with st.sidebar:
        icon_svg = get_icon("shield", size=20, color="#FFFFFF")
        html_brand = f"""
        <div class="ms-sidebar-brand">
            <div class="ms-sidebar-logo-row">
                <div class="ms-sidebar-logo-icon">{icon_svg}</div>
                <div>
                    <div class="ms-sidebar-brand-name">MEDISPACE</div>
                    <div class="ms-sidebar-brand-sub">Clinical Workstation</div>
                </div>
            </div>
            <div style="margin-top: 0.85rem; display: flex; align-items: center; gap: 0.5rem;">
                <span class="ms-badge ms-badge-live">
                    <span class="ms-badge-dot"></span>
                    <span>ONLINE</span>
                </span>
                <span style="font-size: 0.75rem; color: #7DD3FC; font-family: var(--ms-font-mono);">Atlas v7.0</span>
            </div>
        </div>
        """
        st.markdown(html_brand, unsafe_allow_html=True)


def render_workstation_header(
    title: str,
    subtitle: str,
    badge_label: str = "MONGODB CONNECTED",
    badge_status: str = "live",
    icon_name: str = "hospital",
) -> None:
    """Hiển thị Header chuẩn Oceanic Clinical Command Bar."""
    badge_class = f"ms-badge-{badge_status}"
    icon_svg = get_icon(icon_name, size=28, color="#38BDF8")

    html_content = f"""
    <div class="ms-workstation-header">
        <div class="ms-header-brand">
            <div class="ms-header-icon">{icon_svg}</div>
            <div>
                <h1 class="ms-header-title">{html.escape(title)}</h1>
                <p class="ms-header-subtitle">{html.escape(subtitle)}</p>
            </div>
        </div>
        <div class="ms-header-meta">
            <span class="ms-badge {badge_class}">
                <span class="ms-badge-dot"></span>
                <span>{html.escape(badge_label)}</span>
            </span>
            <span class="ms-badge ms-badge-ocean">MONGODB ATLAS · NOSQL</span>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)


def render_kpi_card(
    label: str,
    value: str,
    foot: str,
    icon_name: str = "record",
    accent_color: str = "#0284C7",
) -> None:
    """Hiển thị Card chỉ số KPI y tế phong cách xanh nước biển."""
    icon_svg = get_icon(icon_name, size=18, color=accent_color)
    html_card = f"""
    <div class="ms-kpi-card">
        <div class="ms-kpi-top">
            <span class="ms-kpi-label">{html.escape(label)}</span>
            <div class="ms-kpi-icon">{icon_svg}</div>
        </div>
        <div class="ms-kpi-value">{html.escape(value)}</div>
        <div class="ms-kpi-foot">{html.escape(foot)}</div>
    </div>
    """
    st.markdown(html_card, unsafe_allow_html=True)


def render_workstation_footer() -> None:
    """Footer chuẩn của hệ thống."""
    st.markdown(
        """
        <div class="ms-workstation-footer">
            MediSpace Electronic Health Records · Oceanic Clinical Workstation · MongoDB Document Store
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_pagination(
    total_items: int,
    page_size: int,
    session_key: str = "current_page",
) -> tuple[int, int]:
    """
    Hiển thị bộ điều khiển phân trang Oceanic Clinical Workstation.
    Mỗi trang hiển thị tối đa 50 hồ sơ.
    Trả về (current_page, skip).
    """
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    jump_key = f"{session_key}_jump_txt"

    if session_key not in st.session_state:
        st.session_state[session_key] = 1

    # Đảm bảo trang hiện tại nằm trong giới hạn hợp lệ
    if st.session_state[session_key] > total_pages:
        st.session_state[session_key] = total_pages
    if st.session_state[session_key] < 1:
        st.session_state[session_key] = 1

    current_page = st.session_state[session_key]
    if jump_key not in st.session_state or str(st.session_state[jump_key]) != str(current_page):
        st.session_state[jump_key] = str(current_page)

    skip = (current_page - 1) * page_size

    if total_pages <= 1:
        return current_page, skip

    def _set_page(target_p: int):
        target_p = max(1, min(total_pages, target_p))
        st.session_state[session_key] = target_p
        st.session_state[jump_key] = str(target_p)

    def _on_jump():
        raw_val = str(st.session_state.get(jump_key, "")).strip()
        if raw_val.isdigit():
            p = int(raw_val)
            _set_page(p)
        else:
            st.session_state[jump_key] = str(st.session_state[session_key])

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    c_first, c_prev, c_center, c_next, c_last = st.columns([1.1, 1.2, 3.2, 1.2, 1.1])

    with c_first:
        st.button(
            "« Đầu",
            key=f"{session_key}_btn_first",
            disabled=(current_page <= 1),
            use_container_width=True,
            on_click=_set_page,
            args=(1,),
        )

    with c_prev:
        st.button(
            "‹ Trước",
            key=f"{session_key}_btn_prev",
            disabled=(current_page <= 1),
            use_container_width=True,
            on_click=_set_page,
            args=(current_page - 1,),
        )

    with c_center:
        col_txt1, col_inp, col_txt2 = st.columns([1.2, 1.6, 1.2])
        with col_txt1:
            st.markdown(
                """
                <div style="text-align: right; padding-top: 8px; font-weight: 600; color: var(--ms-text-muted); font-size: 0.9rem;">
                    Trang
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_inp:
            st.text_input(
                "Trang hiện tại",
                key=jump_key,
                on_change=_on_jump,
                label_visibility="collapsed",
                max_chars=6,
            )
        with col_txt2:
            st.markdown(
                f"""
                <div style="text-align: left; padding-top: 8px; font-weight: 700; color: var(--ms-text-title); font-size: 0.9rem;">
                    / {total_pages}
                </div>
                """,
                unsafe_allow_html=True,
            )

    with c_next:
        st.button(
            "Sau ›",
            key=f"{session_key}_btn_next",
            disabled=(current_page >= total_pages),
            use_container_width=True,
            on_click=_set_page,
            args=(current_page + 1,),
        )

    with c_last:
        st.button(
            "Cuối »",
            key=f"{session_key}_btn_last",
            disabled=(current_page >= total_pages),
            use_container_width=True,
            on_click=_set_page,
            args=(total_pages,),
        )

    return current_page, skip
