"""
Clinical De-Identification — Health Universe deployment
Calls the live Render API.
"""

import requests
import streamlit as st

API = "https://clinical-deidentify.onrender.com"
HEADERS = {"Content-Type": "application/json", "X-HU-App": "1"}

st.set_page_config(
    page_title="Clinical De-Identification",
    page_icon="🔒",
    layout="wide",
)

st.title("🔒 Clinical De-Identification")
st.caption("Fast PHI removal from clinical text — names, dates, MRNs, SSNs, addresses and more")

try:
    h = requests.get(f"{API}/health", timeout=8).json()
    loaded = h.get("model_loaded", False)
    status = "✅ Ready" if loaded else "⚡ Regex pipeline active (transformer loading)"
    st.success(f"Service online · {status}")
except Exception:
    st.warning("⚠️ Service may be waking up (free tier). Refresh in 30s.")

st.divider()

tab1, tab2, tab3 = st.tabs(["📝 Text Input", "📄 File Upload", "⚡ Batch"])

# ── Tab 1: Single text ─────────────────────────────────────────────────────────
with tab1:
    st.subheader("De-identify Clinical Text")

    col1, col2 = st.columns([3, 1])
    with col1:
        text_input = st.text_area(
            "Paste clinical note or report",
            height=220,
            placeholder=(
                "e.g. Patient Jane Doe, DOB 03/22/1965, MRN 8821033, "
                "presented to Dr. Smith at MGH on 12/01/2024 with complaints of chest pain. "
                "Phone: 617-555-0182. SSN: 123-45-6789."
            ),
        )
    with col2:
        mode = st.selectbox("Mode", ["mask", "redact", "replace"], index=0)
        st.caption(
            "**mask** — replaces with `[TYPE]`\n\n"
            "**redact** — removes entirely\n\n"
            "**replace** — substitutes realistic fake values"
        )
        run_btn = st.button("De-identify", type="primary", use_container_width=True)

    if run_btn:
        if not text_input.strip():
            st.warning("Paste some text first.")
        else:
            with st.spinner("Processing…"):
                try:
                    resp = requests.post(
                        f"{API}/deidentify",
                        json={"text": text_input, "mode": mode},
                        headers=HEADERS,
                        timeout=30,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.subheader("Original")
                            st.text_area("", value=data.get("original", ""), height=200, disabled=True, key="orig")
                        with col_b:
                            st.subheader("De-identified")
                            st.text_area("", value=data.get("deidentified", ""), height=200, disabled=True, key="deid")

                        entities = data.get("entities", [])
                        if entities:
                            with st.expander(f"🏷️ {len(entities)} PHI entities detected"):
                                for e in entities:
                                    conf = e.get("confidence", 0)
                                    bar = "🟢" if conf > 0.8 else ("🟡" if conf > 0.5 else "🔴")
                                    st.markdown(
                                        f"{bar} `{e.get('text','')}` → **{e.get('label','')}** "
                                        f"(confidence: {conf:.0%})"
                                    )
                    elif resp.status_code == 503:
                        st.info("Pipeline loading — try again in a moment.")
                    else:
                        st.error(f"Error {resp.status_code}: {resp.text[:300]}")
                except Exception as ex:
                    st.error(f"Error: {ex}")

# ── Tab 2: File upload ─────────────────────────────────────────────────────────
with tab2:
    st.subheader("De-identify a Document")
    st.caption("Supports PDF, DOCX, and plain text files.")

    mode_file = st.selectbox("Mode", ["mask", "redact", "replace"], index=0, key="file_mode")
    uploaded = st.file_uploader("Upload clinical document", type=["txt", "pdf", "docx"])

    if uploaded and st.button("De-identify File", type="primary"):
        with st.spinner("Processing file…"):
            try:
                files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
                resp = requests.post(
                    f"{API}/deidentify/file",
                    files=files,
                    params={"mode": mode_file},
                    timeout=60,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.subheader("De-identified Output")
                    st.text_area("Result", value=data.get("deidentified", ""), height=300)
                    entities = data.get("entities", [])
                    st.info(f"Removed {len(entities)} PHI entities.")
                    st.download_button(
                        "Download de-identified text",
                        data=data.get("deidentified", ""),
                        file_name=f"deid_{uploaded.name}.txt",
                        mime="text/plain",
                    )
                elif resp.status_code == 503:
                    st.info("Pipeline loading — try again in a moment.")
                else:
                    st.error(f"Error {resp.status_code}: {resp.text[:300]}")
            except Exception as ex:
                st.error(f"Error: {ex}")

# ── Tab 3: Batch ───────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Batch De-identification")
    st.caption("Process multiple notes at once — one per line.")

    batch_input = st.text_area(
        "Enter notes (one per line)",
        height=250,
        placeholder=(
            "Patient John Smith, MRN 1234, DOB 01/01/1970\n"
            "Referred by Dr. Adams at Boston Medical on 2/14/2024\n"
            "Contact: mary.jones@email.com, Phone 555-0100"
        ),
    )
    mode_batch = st.selectbox("Mode", ["mask", "redact", "replace"], index=0, key="batch_mode")

    if st.button("Run Batch", type="primary"):
        notes = [n.strip() for n in batch_input.splitlines() if n.strip()]
        if not notes:
            st.warning("Enter at least one note.")
        else:
            with st.spinner(f"Processing {len(notes)} notes…"):
                try:
                    resp = requests.post(
                        f"{API}/batch",
                        json={"texts": notes, "mode": mode_batch},
                        headers=HEADERS,
                        timeout=60,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        results = data.get("results", [])
                        st.success(f"✅ Processed {len(results)} notes")
                        for i, r in enumerate(results, 1):
                            with st.expander(f"Note {i} — {len(r.get('entities',[]))} entities removed"):
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.text_area("Original", value=r.get("original", ""), height=120, disabled=True, key=f"bo{i}")
                                with col_b:
                                    st.text_area("De-identified", value=r.get("deidentified", ""), height=120, disabled=True, key=f"bd{i}")
                    elif resp.status_code == 503:
                        st.info("Pipeline loading — try again in a moment.")
                    else:
                        st.error(f"Error {resp.status_code}: {resp.text[:300]}")
                except Exception as ex:
                    st.error(f"Error: {ex}")

st.divider()
st.caption("Powered by [Clinical-Deidentify](https://clinical-deidentify.onrender.com/docs) · x402/MPP payment protocol")
