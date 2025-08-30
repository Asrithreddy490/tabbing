from imports import*
from core.io_utils import probe_file_like, load_data  # reuse your pipeline loader

def render_file_checker_tab():
    st.header("🧪 Check Data File Compatibility")

    uploaded = st.file_uploader(
        "Upload a data file (.csv, .xls, .xlsx)",
        type=["csv", "xls", "xlsx"]
    )

    st.caption(
        "Excel requires **openpyxl** (.xlsx) / **xlrd** (.xls). "
        "If missing, you'll see a helpful error."
    )

    if uploaded is None:
        return

    # First: raw read (fast). Offer optional full pipeline in UI below.
    res = probe_file_like(uploaded, run_full_pipeline=False)

    if res["ok"]:
        st.success(f"✅ {res['msg']}")
        st.write(f"**File:** `{res['name']}`  |  **Format:** `{res['ext']}`")
        st.write(f"**Shape:** {res['df'].shape[0]} rows × {res['df'].shape[1]} columns")

        st.subheader("Preview (first 10 rows)")
        st.dataframe(res["df"].head(10), use_container_width=True)

        with st.expander("📚 Columns"):
            st.write(list(res["df"].columns))

        with st.expander("Advanced: Try full pipeline load (cleaning only)"):
            if st.button("Run full pipeline check"):
                try:
                    import os
                    temp_path = f"__pipeline__{res['name']}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded.getbuffer())
                    full_df = load_data(temp_path)
                    st.success("✅ Full pipeline load succeeded.")
                    st.write(f"Cleaned shape: {full_df.shape}")
                except Exception as e:
                    st.error(f"❌ Full pipeline load failed: {e}")
                finally:
                    try:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    except Exception:
                        pass

    else:
        st.error(f"❌ {res['msg']}")
