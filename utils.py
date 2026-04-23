import io
import pandas as pd
import zipfile
import json
import streamlit as st
from typing import Dict, List
from urllib import parse, request

def file_id(file_name: str) -> str:
    return file_name.replace(" ", "_").replace(".", "_")

def session_key(p: str, n: str) -> str: 
    return f"{p}_{file_id(n)}"

def escape_markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")

def dataframe_to_markdown(df: pd.DataFrame) -> str:
    prep = df.copy().fillna("").astype(str)
    headers = [escape_markdown_cell(c) for c in prep.columns]
    h_row = "| " + " | ".join(headers) + " |"
    s_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    b_rows = ["| " + " | ".join([escape_markdown_cell(c) for c in r]) + " |" for r in prep.values]
    return "\n".join([h_row, s_row, *b_rows])

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    c = df.copy()
    c = c.apply(lambda col: col.map(lambda v: v.strip() if isinstance(v, str) else v))
    c.replace(r"^\s*$", pd.NA, regex=True, inplace=True)
    c.dropna(how="all", inplace=True)
    c.dropna(axis=1, how="all", inplace=True)
    return c

def load_workbook(uf: io.BytesIO) -> Dict[str, pd.DataFrame]:
    wb = pd.read_excel(uf, sheet_name=None, engine="openpyxl")
    res = {}
    for sn, df in wb.items():
        cdf = clean_dataframe(df)
        if not cdf.empty: res[sn] = cdf
    return res

def filter_dataframe(df: pd.DataFrame, q: str) -> pd.DataFrame:
    if not q: return df
    low = q.casefold()
    mask = df.astype(str).apply(lambda r: r.str.casefold().str.contains(low, na=False).any(), axis=1)
    return df[mask]

def combined_markdown(sheets: List[str], wb: Dict[str, pd.DataFrame]) -> str:
    s = [f"## {n}\n\n{dataframe_to_markdown(wb[n]).strip()}" for n in sheets]
    return "\n\n".join(s).strip()

def sync_markdown_state(name: str, md: str, sheets: List[str]):
    sig_k, gen_k, con_k, edt_k, mod_k = [session_key(p, name) for p in ["sig","gen","md_content","editor_text","md_mode"]]
    sig = tuple(sheets)
    if st.session_state.get(sig_k) != sig:
        st.session_state[sig_k], st.session_state[gen_k], st.session_state[con_k], st.session_state[edt_k] = sig, md, md, md
    st.session_state.setdefault(gen_k, md)
    st.session_state.setdefault(con_k, md)
    st.session_state.setdefault(mod_k, "Editor")
    st.session_state.setdefault(edt_k, st.session_state[con_k])

def sync_editor_to_markdown(name: str):
    st.session_state[session_key("md_content", name)] = st.session_state.get(session_key("editor_text", name), "")

def sync_markdown_to_editor(name: str):
    st.session_state[session_key("editor_text", name)] = st.session_state.get(session_key("md_content", name), "")

def build_zip_archive(files: Dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as arc:
        for n, m in files.items(): arc.writestr(n, m.encode("utf-8"))
    return buf.getvalue()

def build_merged_workbooks_markdown(names: List[str], outs: Dict[str, str]) -> str:
    s = [f"# {n.rsplit('.', 1)[0]}\n\n{outs[n].strip()}" for n in names if outs.get(n, "").strip()]
    return "\n\n".join(s).strip()

def translate_markdown_content(text: str, translator) -> str:
    return "\n".join(translate_markdown_line(l, translator) for l in text.splitlines())

def translate_markdown_line(l: str, trans) -> str:
    s = l.strip()
    if not s or (s.startswith("|") and s.endswith("|") and all(set(c.strip()) <= {":", "-"} for c in s.strip("|").split("|"))): return l
    if s.startswith("|") and s.endswith("|"):
        cells = [c.strip() for c in s[1:-1].split("|")]
        t_cells = [f" {escape_markdown_cell(trans(c))} " if c else " " for c in cells]
        return f"|{'|'.join(t_cells)}|"
    if s.startswith("#"):
        pre = l[:len(l)-len(l.lstrip())]
        marks = s[:len(s)-len(s.lstrip("#"))]
        txt = s[len(marks):].strip()
        return f"{pre}{marks} {trans(txt)}" if txt else l
    return trans(l)

def deepl_translate(t: str, k: str, tl: str) -> str:
    try:
        p = parse.urlencode({"text": t, "target_lang": tl.upper(), "tag_handling": "html"}).encode("utf-8")
        req = request.Request("https://api-free.deepl.com/v2/translate", data=p, headers={"Authorization": f"DeepL-Auth-Key {k}"})
        with request.urlopen(req) as r: return json.loads(r.read())["translations"][0]["text"]
    except: return f"[DeepL Error] {t}"

def google_translate(t: str, k: str, tl: str) -> str:
    try:
        u = f"https://translation.googleapis.com/language/translate/v2?key={k}"
        p = json.dumps({"q": t, "target": tl.lower(), "format": "text"}).encode("utf-8")
        req = request.Request(u, data=p, headers={"Content-Type": "application/json"})
        with request.urlopen(req) as r: return json.loads(r.read())["data"]["translations"][0]["translatedText"]
    except: return f"[Google Error] {t}"

def translate_text(t: str, dk: str, gk: str, tl: str) -> str:
    if dk: return translate_markdown_content(t, lambda c: deepl_translate(c, dk, tl))
    if gk: return translate_markdown_content(t, lambda c: google_translate(c, gk, tl))
    raise ValueError("Add API Key")
