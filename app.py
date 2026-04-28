import streamlit as st
import pandas as pd
import json
from typing import Dict, List
from utils import (
    load_workbook, combined_markdown, build_zip_archive, 
    build_merged_workbooks_markdown, filter_dataframe, session_key,
    sync_markdown_state, sync_editor_to_markdown, sync_markdown_to_editor,
    translate_text
)
from styles import apply_custom_styles

st.set_page_config(page_title="XLSX to Markdown", page_icon=":page_facing_up:", layout="wide", initial_sidebar_state="collapsed")

# --- UI COMPONENTS ---

def render_header(active_md, active_name, merged_md, outputs, file_names):
    t_col, a_col = st.columns([2, 1])
    with t_col:
        st.title("XLSX to Markdown")
        st.caption("XLSX to MD with live preview.")
    
    with a_col:
        # Create a container that aligns buttons to the right
        st.write('<div class="header-actions">', unsafe_allow_html=True)
        cols = st.columns([1, 1, 1]) # Three small columns at the end
        
        # Current button
        if active_md.strip():
            with cols[0]:
                st.download_button("Current", data=active_md.encode("utf-8"), file_name=f"{active_name.rsplit('.', 1)[0]}.md", use_container_width=True)
        
        # ZIP button
        z_payload = {f"{n.rsplit('.', 1)[0]}.md": md for n, md in outputs.items() if md.strip()}
        if z_payload:
            with cols[1]:
                st.download_button("ZIP", data=build_zip_archive(z_payload), file_name="xlsx-to-markdown.zip", use_container_width=True)
        
        # Merged button
        if len(file_names) > 1 and merged_md.strip():
            with cols[2]:
                st.download_button("Merged", data=merged_md.encode("utf-8"), file_name="all-workbooks.md", use_container_width=True)
        st.write('</div>', unsafe_allow_html=True)

def render_sheet_multiselects(names, wbs):
    res = {}
    for i in range(0, len(names), 2):
        batch, cols = names[i:i+2], st.columns(min(len(names[i:i+2]), 2))
        for c, n in zip(cols, batch):
            with c: res[n] = st.multiselect(f"Sheets - {n}", options=list(wbs[n].keys()), default=list(wbs[n].keys()), key=session_key("sel", n))
    return res

# --- APP START ---
apply_custom_styles()

# 1. RESERVE TOP SLOT FOR HEADER
header_area = st.empty()

# 2. UPLOADER (NOW PHYSICALLY BELOW HEADER)
st.subheader("Workbooks")
uploaded_files = st.file_uploader("Upload XLSX", type=["xlsx"], accept_multiple_files=True, key="uploader_top", label_visibility="collapsed")

# 3. PRE-PROCESS DATA
workbooks = {}
file_names = []
active_n = ""
active_md = ""
outputs = {}
merged_md = ""
selected_sheets = {}

if uploaded_files:
    for f in uploaded_files:
        try:
            wb = load_workbook(f)
            if wb: workbooks[f.name] = wb
        except: continue

    if workbooks:
        file_names = list(workbooks.keys())
        st.session_state.setdefault("active_workbook", file_names[0])
        if st.session_state["active_workbook"] not in file_names:
            st.session_state["active_workbook"] = file_names[0]
        
        # Capture selection
        with st.container(border=True):
            selected_sheets = render_sheet_multiselects(file_names, workbooks)
        
        # Sync states
        for n in file_names:
            sel = selected_sheets.get(n, [])
            if sel: sync_markdown_state(n, combined_markdown(sel, workbooks[n]), sel)

        # Build final strings
        active_n = st.session_state["active_workbook"]
        active_md = st.session_state.get(session_key("md_content", active_n), "")
        outputs = {n: st.session_state.get(session_key("md_content", n), "") for n in file_names}
        merged_md = build_merged_workbooks_markdown(file_names, outputs)

# 4. NOW RENDER THE HEADER INTO THE TOP SLOT
with header_area:
    render_header(active_md, active_n, merged_md, outputs, file_names)

if not uploaded_files:
    st.info("Upload XLSX to start.")
    st.stop()

# 5. RENDER PREVIEW/EDITOR
l_col, r_col = st.columns(2)
with l_col:
    st.subheader("Excel Data")
    with st.container(border=True):
        st.selectbox("Workbook", options=file_names, key="active_workbook")
        active_n = st.session_state["active_workbook"]
        sel = selected_sheets.get(active_n, [])
        if not sel: st.stop()
        pk = session_key("preview_sheet", active_n)
        if st.session_state.get(pk) not in sel: st.session_state[pk] = sel[0]
        st.selectbox("Worksheet", options=sel, key=pk)
        st.text_input("Search", key=session_key("search", active_n))
    st.dataframe(filter_dataframe(workbooks[active_n][st.session_state[pk]], st.session_state.get(session_key("search", active_n), "")), use_container_width=True, height=500)

with r_col:
    st.subheader("Markdown")
    mk, ak, ek = session_key("md_content", active_n), session_key("md_mode", active_n), session_key("editor_text", active_n)
    with st.container(border=True):
        m_col, c_col = st.columns([3, 1])
        with m_col: st.radio("Mode", options=["Editor", "View"], key=ak, horizontal=True, label_visibility="collapsed")
        with c_col:
            # Client-side copy button to avoid lag and reruns
            html_copy = f"""
                <button id="copy-btn" style="width:100%; height:2.4rem; border-radius:8px; background-color:#1e293b; color:white; border:1px solid rgba(255,255,255,0.1); cursor:pointer; font-size:14px; transition:all 0.2s ease;">Copy</button>
                <script>
                    document.getElementById('copy-btn').onclick = function() {{
                        const text = {json.dumps(st.session_state.get(mk, ""))};
                        navigator.clipboard.writeText(text).then(() => {{
                            this.innerText = 'Copied!';
                            this.style.backgroundColor = '#2563eb';
                            setTimeout(() => {{
                                this.innerText = 'Copy';
                                this.style.backgroundColor = '#1e293b';
                            }}, 2000);
                        }}).catch(err => {{
                            console.error('Copy failed', err);
                            alert('Copy failed. Please try again.');
                        }});
                    }};
                </script>
            """
            st.components.v1.html(html_copy, height=45)
        
        with st.expander("Settings & Translation"):
            deepl_k = st.text_input("DeepL API Key", type="password")
            google_k = st.text_input("Google Translate API Key", type="password")
            target_l = st.text_input("Target Language", value="EN")

        if st.session_state[ak] == "Editor":
            st.text_area("Editor", key=ek, height=400, on_change=sync_editor_to_markdown, args=(active_n,))
            st.session_state[mk] = st.session_state.get(ek, "")
            if st.button("Translate"):
                st.session_state[mk] = translate_text(st.session_state.get(ek, ""), deepl_k, google_k, target_l)
                sync_markdown_to_editor(active_n)
                st.rerun()
        else:
            st.markdown(st.session_state.get(mk, "") or "_No content._")