import json
import glob
import os

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


def find_data_dir(base="Dataset"):
    candidates = glob.glob(os.path.join(base, "E-Commerce Dataset*"))
    if candidates:
        return candidates[0]
    if os.path.isdir(base):
        return base
    raise FileNotFoundError("Dataset directory not found")


def load_data(data_dir):
    data = {}
    for path in glob.glob(os.path.join(data_dir, "*.csv")):
        name = os.path.splitext(os.path.basename(path))[0]
        try:
            df = pd.read_csv(path, low_memory=False)
        except Exception:
            df = pd.read_csv(path, encoding="latin1", low_memory=False)
        data[name] = df
    return data


@st.cache_data
def get_dataset():
    data_dir = find_data_dir()
    data = load_data(data_dir)
    for df in data.values():
        for col in df.columns:
            if "date" in col or "timestamp" in col:
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                except Exception:
                    pass
    return data


def build_er_model(data_dict):
    all_columns = {}
    for table_name, df in data_dict.items():
        for col in df.columns:
            all_columns.setdefault(col.lower(), []).append(table_name)

    tables = []
    relationships = []
    seen_relations = set()

    for index, (table_name, df) in enumerate(data_dict.items()):
        columns = []
        for col in df.columns:
            lower = col.lower()
            if lower == "id" or lower == f"{table_name.lower()}_id" or lower == f"{table_name.lower()[:-1]}_id":
                tag = "PK"
            elif lower.endswith("_id") and len(all_columns.get(lower, [])) > 1:
                tag = "FK"
            else:
                tag = ""

            columns.append({
                "name": col,
                "type": str(df[col].dtype),
                "tag": tag,
            })

        tables.append({
            "name": table_name,
            "id": table_name,
            "x": 260 + (index % 3) * 420,
            "y": 180 + (index // 3) * 260,
            "columns": columns,
        })

    for table_name, df in data_dict.items():
        for col in df.columns:
            lower = col.lower()
            if not lower.endswith("_id") and lower != "id":
                continue
            for other_name, other_df in data_dict.items():
                if other_name == table_name:
                    continue
                if col in other_df.columns:
                    key = tuple(sorted((table_name, other_name, col.lower())))
                    if key in seen_relations:
                        continue
                    seen_relations.add(key)
                    relationships.append({
                        "source": table_name,
                        "target": other_name,
                        "label": col,
                    })

    return {"tables": tables, "relationships": relationships}


def render_er_diagram(data_dict):
    er_model = build_er_model(data_dict)
    er_json = json.dumps(er_model)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                background: #f8fafc;
                color: #111827;
                overflow: hidden;
            }}
            .app {{
                height: 650px;
                display: flex;
                border: 1px solid #e5e7eb;
                border-radius: 14px;
                overflow: hidden;
                background: white;
            }}
            .sidebar {{
                width: 230px;
                flex-shrink: 0;
                border-right: 1px solid #e5e7eb;
                background: #ffffff;
                padding: 18px;
                z-index: 20;
            }}
            .title {{ font-size: 16px; font-weight: 700; margin-bottom: 4px; }}
            .subtitle {{ font-size: 12px; color: #6b7280; margin-bottom: 18px; }}
            .search {{
                width: 100%;
                padding: 9px 11px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                outline: none;
                font-size: 13px;
                margin-bottom: 16px;
            }}
            .search:focus {{ border-color: #f97316; }}
            .section {{
                margin-top: 15px;
                margin-bottom: 8px;
                font-size: 11px;
                font-weight: 700;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: .05em;
            }}
            .table-item {{
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 7px 4px;
                font-size: 13px;
                cursor: pointer;
                border-radius: 6px;
            }}
            .table-item:hover {{ background: #f3f4f6; }}
            .table-item input {{ accent-color: #f97316; }}
            .canvas {{
                position: relative;
                flex: 1;
                overflow: hidden;
                background-color: #f8fafc;
                background-image: radial-gradient(#d1d5db 1px, transparent 1px);
                background-size: 20px 20px;
                cursor: grab;
            }}
            .canvas.dragging {{ cursor: grabbing; }}
            .world {{
                position: absolute;
                left: 0;
                top: 0;
                width: 2200px;
                height: 1400px;
                transform-origin: 0 0;
            }}
            .table {{
                position: absolute;
                width: 240px;
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 10px;
                box-shadow: 0 5px 18px rgba(0,0,0,.07);
                overflow: hidden;
                cursor: move;
                user-select: none;
            }}
            .table.selected {{ border-color: #f97316; box-shadow: 0 0 0 2px rgba(249,115,22,.15); }}
            .table-header {{
                padding: 11px 13px;
                background: #111827;
                color: white;
                font-weight: 700;
                font-size: 13px;
            }}
            .columns {{ padding: 6px 0; }}
            .column {{
                display: flex;
                align-items: center;
                padding: 6px 12px;
                font-size: 12px;
                gap: 8px;
                min-width: 0;
            }}
            .column:hover {{ background: #f9fafb; }}
            .badge {{
                font-size: 9px;
                font-weight: 800;
                padding: 2px 4px;
                border-radius: 4px;
                min-width: 22px;
                text-align: center;
                flex-shrink: 0;
            }}
            .pk {{ background: #fef3c7; color: #92400e; }}
            .fk {{ background: #dbeafe; color: #1e40af; }}
            .column-name {{
                flex: 1;
                min-width: 0;
                overflow-wrap: anywhere;
                word-break: break-word;
            }}
            .type {{
                color: #9ca3af;
                font-size: 10px;
                flex-shrink: 0;
            }}
            svg {{
                position: absolute;
                left: 0;
                top: 0;
                width: 2200px;
                height: 1400px;
                pointer-events: none;
                overflow: visible;
            }}
            .relationship {{ stroke: #9ca3af; stroke-width: 2; fill: none; }}
            .relationship-label {{ font-size: 11px; fill: #6b7280; }}
            .controls {{
                position: absolute;
                right: 15px;
                bottom: 15px;
                display: flex;
                gap: 5px;
                background: white;
                border: 1px solid #e5e7eb;
                padding: 5px;
                border-radius: 9px;
                box-shadow: 0 4px 15px rgba(0,0,0,.08);
                z-index: 30;
            }}
            button {{
                border: 0;
                background: white;
                width: 32px;
                height: 30px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 15px;
            }}
            button:hover {{ background: #f3f4f6; }}
            .zoom-label {{
                width: 45px;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 11px;
                color: #6b7280;
            }}
        </style>
    </head>
    <body>
        <div class="app">
            <aside class="sidebar">
                <div class="title">Database Explorer</div>
                <div class="subtitle">Interactive ER Diagram</div>
                <input class="search" id="search" placeholder="🔍 Search tables...">
                <div class="section">Tables</div>
                <div id="tableList"></div>
                <div class="section">Filters</div>
                <label class="table-item"><input type="checkbox" id="showPK" checked>Show primary keys</label>
                <label class="table-item"><input type="checkbox" id="showFK" checked>Show foreign keys</label>
            </aside>

            <main class="canvas" id="canvas">
                <div class="world" id="world">
                    <svg id="connections"></svg>
                </div>
                <div class="controls">
                    <button onclick="zoomOut()">−</button>
                    <div class="zoom-label" id="zoomLabel">100%</div>
                    <button onclick="zoomIn()">+</button>
                    <button onclick="resetView()">⌂</button>
                </div>
            </main>
        </div>

        <script>
            const erData = {er_json};
            const canvas = document.getElementById("canvas");
            const world = document.getElementById("world");
            const svg = document.getElementById("connections");
            const tableList = document.getElementById("tableList");
            let scale = 1;
            let panX = 0;
            let panY = 0;
            let draggingCanvas = false;
            let startX;
            let startY;

            function buildTables() {{
                tableList.innerHTML = "";
                erData.tables.forEach((table) => {{
                    const label = document.createElement("label");
                    label.className = "table-item";
                    label.innerHTML = `<input type="checkbox" checked data-table="${{table.id}}">${{table.name}}`;
                    tableList.appendChild(label);
                }});

                erData.tables.forEach((table) => {{
                    const tableEl = document.createElement("div");
                    tableEl.className = "table";
                    tableEl.id = table.id;
                    tableEl.style.left = table.x + "px";
                    tableEl.style.top = table.y + "px";

                    const header = document.createElement("div");
                    header.className = "table-header";
                    header.textContent = table.name.toUpperCase();

                    const columnsEl = document.createElement("div");
                    columnsEl.className = "columns";

                    table.columns.forEach((column) => {{
                        const row = document.createElement("div");
                        row.className = "column";

                        const badge = document.createElement("span");
                        badge.className = "badge " + (column.tag === "PK" ? "pk" : column.tag === "FK" ? "fk" : "");
                        badge.textContent = column.tag || "";
                        if (!column.tag) badge.style.visibility = "hidden";

                        const name = document.createElement("span");
                        name.className = "column-name";
                        name.textContent = column.name;

                        const type = document.createElement("span");
                        type.className = "type";
                        type.textContent = column.type;

                        row.appendChild(badge);
                        row.appendChild(name);
                        row.appendChild(type);
                        columnsEl.appendChild(row);
                    }});

                    tableEl.appendChild(header);
                    tableEl.appendChild(columnsEl);
                    world.appendChild(tableEl);
                }});

                attachTableInteraction();
                drawConnections();
            }}

            function attachTableInteraction() {{
                document.querySelectorAll(".table").forEach((table) => {{
                    let dragging = false;
                    let offsetX = 0;
                    let offsetY = 0;

                    table.addEventListener("mousedown", (e) => {{
                        dragging = true;
                        table.classList.add("selected");
                        offsetX = e.clientX / scale - table.offsetLeft - panX / scale;
                        offsetY = e.clientY / scale - table.offsetTop - panY / scale;
                        e.stopPropagation();
                    }});

                    document.addEventListener("mousemove", (e) => {{
                        if (!dragging) return;
                        const x = e.clientX / scale - offsetX - panX / scale;
                        const y = e.clientY / scale - offsetY - panY / scale;
                        table.style.left = x + "px";
                        table.style.top = y + "px";
                        drawConnections();
                    }});

                    document.addEventListener("mouseup", () => {{ dragging = false; }});
                }});
            }}

            function drawConnections() {{
                svg.innerHTML = "";

                erData.relationships.forEach((rel) => {{
                    const a = document.getElementById(rel.source);
                    const b = document.getElementById(rel.target);
                    if (!a || !b) return;
                    if (a.style.display === "none" || b.style.display === "none") return;

                    const ax = a.offsetLeft + a.offsetWidth;
                    const ay = a.offsetTop + a.offsetHeight / 2;
                    const bx = b.offsetLeft;
                    const by = b.offsetTop + b.offsetHeight / 2;

                    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                    line.setAttribute("x1", ax);
                    line.setAttribute("y1", ay);
                    line.setAttribute("x2", bx);
                    line.setAttribute("y2", by);
                    line.setAttribute("class", "relationship");
                    svg.appendChild(line);

                    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
                    text.setAttribute("x", (ax + bx) / 2);
                    text.setAttribute("y", (ay + by) / 2 - 7);
                    text.setAttribute("class", "relationship-label");
                    text.textContent = rel.label;
                    svg.appendChild(text);
                }});
            }}

            tableList.addEventListener("change", (e) => {{
                if (!e.target.dataset.table) return;
                const table = document.getElementById(e.target.dataset.table);
                if (!table) return;
                table.style.display = e.target.checked ? "block" : "none";
                drawConnections();
            }});

            document.getElementById("search").addEventListener("input", (e) => {{
                const query = e.target.value.toLowerCase();
                document.querySelectorAll(".table").forEach((table) => {{
                    table.style.display = table.id.toLowerCase().includes(query) ? "block" : "none";
                }});
                tableList.querySelectorAll("input[data-table]").forEach((input) => {{
                    const table = document.getElementById(input.dataset.table);
                    input.checked = table && table.style.display !== "none";
                }});
                drawConnections();
            }});

            document.getElementById("showPK").addEventListener("change", (e) => {{
                document.querySelectorAll(".pk").forEach((el) => {{
                    el.style.display = e.target.checked ? "inline-block" : "none";
                }});
            }});

            document.getElementById("showFK").addEventListener("change", (e) => {{
                document.querySelectorAll(".fk").forEach((el) => {{
                    el.style.display = e.target.checked ? "inline-block" : "none";
                }});
            }});

            function zoomIn() {{
                scale = Math.min(scale + 0.1, 2);
                updateTransform();
            }}

            function zoomOut() {{
                scale = Math.max(scale - 0.1, 0.4);
                updateTransform();
            }}

            function resetView() {{
                scale = 1;
                panX = 0;
                panY = 0;
                updateTransform();
            }}

            function updateTransform() {{
                world.style.transform = `translate(${{panX}}px, ${{panY}}px) scale(${{scale}})`;
                document.getElementById("zoomLabel").textContent = Math.round(scale * 100) + "%";
            }}

            canvas.addEventListener("mousedown", (e) => {{
                if (e.target.closest(".table")) return;
                draggingCanvas = true;
                canvas.classList.add("dragging");
                startX = e.clientX - panX;
                startY = e.clientY - panY;
            }});

            canvas.addEventListener("mousemove", (e) => {{
                if (!draggingCanvas) return;
                panX = e.clientX - startX;
                panY = e.clientY - startY;
                updateTransform();
            }});

            canvas.addEventListener("mouseup", () => {{
                draggingCanvas = false;
                canvas.classList.remove("dragging");
            }});

            document.addEventListener("mouseleave", () => {{
                draggingCanvas = false;
                canvas.classList.remove("dragging");
            }});

            buildTables();
            updateTransform();
        </script>
    </body>
    </html>
    """

    components.html(html, height=700, scrolling=False)


def render_data_tab():
    try:
        data = get_dataset()
    except FileNotFoundError:
        st.error("Dataset folder not found. Make sure the `Dataset/E-Commerce Dataset` directory exists.")
        st.stop()

    st.subheader("Dataset overview")
    overview = []
    for name, df in data.items():
        overview.append({"Table": name, "Rows": len(df), "Columns": len(df.columns)})
    st.table(pd.DataFrame(overview).set_index("Table"))

    st.markdown("---")
    st.subheader("Data model (ER diagram)")
    render_er_diagram(data)

    st.markdown("---")
    st.subheader("Data dictionary and sample views")
    for name, df in data.items():
        with st.expander(f"{name} ({len(df.columns)} fields, {len(df)} rows)"):
            st.write("Columns:")
            columns = pd.DataFrame({"name": df.columns, "dtype": [str(dt) for dt in df.dtypes]})
            st.dataframe(columns)
            st.write("Sample rows:")
            st.dataframe(df.head(3))
