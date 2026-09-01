import json
import os
import base64
import re

import streamlit as st


LINKS_FILE = "analysis_links.json"

STATUS_STYLE = {
    "Completed":   "background:#dcfce7; color:#15803d; border:1px solid #bbf7d0;",
    "In Progress": "background:#dbeafe; color:#1d4ed8; border:1px solid #bfdbfe;",
    "Pending":     "background:#fef3c7; color:#b45309; border:1px solid #fde68a;",
    "Not Started": "background:#f3f4f6; color:#4b5563; border:1px solid #e5e7eb;",
}

TOPIC_STYLE = {
    "Product & Pricing":     "background:#fff3c4; color:#806800;",
    "Seller Performance":    "background:#d1fae5; color:#065f46;",
    "Delivery Performance":  "background:#dbeafe; color:#1d4ed8;",
    "Regional Logistics":    "background:#fce7f3; color:#9d174d;",
    "Seller Behaviour Drivers": "background:#ede9fe; color:#5b21b6;",
}


def load_links():
    try:
        if not os.path.exists(LINKS_FILE):
            return []
        with open(LINKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _extract_member_name_from_folder(path_value: str) -> str:
    """Infer member name from analysis folder name."""
    if not path_value:
        return ""

    folder = os.path.basename(os.path.dirname(path_value))
    if not folder:
        return ""

    # Supports legacy folder patterns and plain member-name folders.
    dash_match = re.search(r"-\s*([A-Za-z][A-Za-z\s.]*)$", folder)
    if dash_match:
        return dash_match.group(1).strip()

    paren_match = re.search(r"\(([^)]+)\)", folder)
    if paren_match:
        return paren_match.group(1).strip()

    return folder.strip().replace("_", " ").title()


def _derive_member_display(entry: dict) -> tuple[str, str]:
    """Return display name and avatar initial using analysis folder names."""
    path_candidates = [
        entry.get("pdf") or "",
        entry.get("notebook") or "",
        entry.get("html") or "",
        entry.get("figures_dir") or "",
    ]

    display_name = ""
    for path_value in path_candidates:
        display_name = _extract_member_name_from_folder(path_value)
        if display_name:
            break

    if not display_name:
        display_name = entry.get("name", "")

    parts = [p for p in display_name.split() if p]
    if len(parts) >= 2:
        initial = (parts[0][0] + parts[1][0]).upper()
    elif len(parts) == 1:
        initial = parts[0][0].upper()
    else:
        initial = "?"

    return display_name, initial


def pdf_download_button(pdf_path: str, label: str = "Download PDF"):
    """Render an inline base64 PDF download button."""
    if not pdf_path or not os.path.exists(pdf_path):
        return
    with open(pdf_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    filename = os.path.basename(pdf_path)
    href = (
        f'<a href="data:application/pdf;base64,{b64}" '
        f'download="{filename}" '
        f'style="display:inline-flex;align-items:center;gap:6px;'
        f'padding:8px 16px;background:#1d4ed8;color:white;border-radius:8px;'
        f'font-size:13px;font-weight:600;text-decoration:none;">'
        f'⬇ {label}</a>'
    )
    st.markdown(href, unsafe_allow_html=True)


def render_analysis_tab():
    links = load_links()

    if not links:
        st.info("No analysis entries found. Add entries to analysis_links.json.")
        return

    # ── header ──────────────────────────────────────────────────────────────
    st.markdown(
        """
        <style>
        .ana-header { margin-bottom: 8px; }
        .ana-header h2 { font-size:1.6rem; font-weight:750; color:#111827;
                         letter-spacing:-0.5px; margin:0; }
        .ana-header p  { color:#6b7280; font-size:14px; margin:6px 0 0; }

        .ana-card {
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 20px 22px;
            background: #ffffff;
            box-shadow: 0 3px 12px rgba(0,0,0,0.04);
            margin-bottom: 18px;
            position: relative;
            overflow: hidden;
        }
        .ana-card::before {
            content:"";
            position:absolute; left:0; top:0; bottom:0; width:4px;
            background: linear-gradient(180deg,#F58A3D,#ffbd85);
        }
        .ana-card-dimmed { opacity: 0.55; }

        .ana-avatar {
            display:inline-flex; align-items:center; justify-content:center;
            width:42px; height:42px; border-radius:50%;
            background:linear-gradient(135deg,#fff1e6,#ffd7b5);
            color:#d96d20; font-size:14px; font-weight:750;
            border:2px solid white; box-shadow:0 2px 8px rgba(0,0,0,0.08);
            flex-shrink:0;
        }
        .ana-name  { font-size:16px; font-weight:700; color:#111827; }
        .ana-topic { display:inline-block; padding:3px 9px; border-radius:20px;
                     font-size:10px; font-weight:700; margin-left:8px; }
        .ana-status { display:inline-block; padding:3px 10px; border-radius:999px;
                      font-size:11px; font-weight:700; }
        .ana-q { font-size:12.5px; color:#374151; line-height:1.55;
                 margin:4px 0 0 0; }
        .ana-qnum { font-size:10px; font-weight:750; color:#a18d45;
                    margin-right:6px; }
        .ana-links { display:flex; gap:10px; flex-wrap:wrap; margin-top:12px; }
        .ana-link-btn {
            display:inline-flex; align-items:center; gap:5px;
            padding:6px 14px; border-radius:8px; font-size:12px; font-weight:600;
            text-decoration:none; border:1.5px solid #e5e7eb;
            color:#374151; background:#f9fafb; transition:background .15s;
        }
        .ana-link-btn:hover { background:#f3f4f6; }
        .ana-link-btn.primary { background:#1d4ed8; color:#fff; border-color:#1d4ed8; }
        .ana-link-btn.primary:hover { background:#1e40af; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="ana-header">'
        "<h2>Team Analysis</h2>"
        "<p>Each member's notebook, report, and questions answered</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── one card per member ──────────────────────────────────────────────────
    for entry in links:
        name, initial = _derive_member_display(entry)
        topic     = entry.get("topic", "")
        questions = entry.get("questions", [])
        status    = entry.get("status", "Not Started")
        pdf_path  = entry.get("pdf") or ""
        nb_path   = entry.get("notebook") or ""
        html_path = entry.get("html") or ""
        figs_dir  = entry.get("figures_dir") or ""

        completed  = status == "Completed"
        dimmed_cls = "" if completed else " ana-card-dimmed"

        topic_css  = TOPIC_STYLE.get(topic, "background:#f3f4f6; color:#555;")
        status_css = STATUS_STYLE.get(status, STATUS_STYLE["Not Started"])

        qs_html = "".join(
            f'<p class="ana-q"><span class="ana-qnum">Q{i+1}</span>{q}</p>'
            for i, q in enumerate(questions)
        )

        links_html = ""
        if pdf_path and os.path.exists(pdf_path):
            abs_pdf = os.path.abspath(pdf_path)
            links_html += (
                f'<a class="ana-link-btn primary" '
                f'href="file://{abs_pdf}" '
                f'target="_blank" rel="noopener noreferrer">📄 Open PDF</a>'
            )
        if nb_path and os.path.exists(nb_path):
            links_html += (
                f'<a class="ana-link-btn" href="file://{os.path.abspath(nb_path)}" '
                f'target="_blank">📓 Notebook</a>'
            )

        card_html = f"""
        <div class="ana-card{dimmed_cls}">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
            <div class="ana-avatar">{initial}</div>
            <div>
              <span class="ana-name">{name}</span>
              <span class="ana-topic" style="{topic_css}">{topic}</span>
            </div>
            <div style="margin-left:auto;">
              <span class="ana-status" style="{status_css}">{status}</span>
            </div>
          </div>
          {qs_html}
          <div class="ana-links">{links_html}</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
