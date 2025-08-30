# ui/ui_generate_counts.py
from imports import *
from ui.ui_file_formate import render_sample_formate_datamap


def _save_uploaded_file(uploaded_file, prefix="__temp__"):
    """Save an uploaded file to a temp path and return the path."""
    temp_path = f"{prefix}_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_path


def render_generate_counts_tab():
    st.subheader("🔢 Generate Counts")
    data_file_counts = st.file_uploader("Upload Data File", type=["csv", "xls", "xlsx"], key="counts_data")
    datamap_file_counts = st.file_uploader("Upload Datamap Excel (Sheet1)", type=["xls", "xlsx", "xlsm"], key="counts_dm")

    if st.button("⚡ Generate Counts", type="primary", key="btn_counts"):
        if not data_file_counts or not datamap_file_counts:
            st.error("Please upload both Data and Datamap files.")
            st.stop()

        data_temp = _save_uploaded_file(data_file_counts, "counts_data")
        datamap_temp = _save_uploaded_file(datamap_file_counts, "counts_dm")

        try:
            data_df = load_data(data_temp)
            dm_df = pd.read_excel(datamap_temp, sheet_name="Sheet1")
            unresolved = []
            counts_df = compute_counts_from_datamap(dm_df, data_df, unresolved_report=unresolved)

            st.success("✅ Counts generated")
            st.dataframe(counts_df.head(50))

            today = datetime.today().strftime("%Y%m%d")
            excel_name = f"Counts_{today}.xlsx"
            counts_df.to_excel(excel_name, index=False)

            with open(excel_name, "rb") as f:
                st.download_button("⬇️ Download Excel", f, file_name=excel_name)

            st.download_button(
                "⬇️ Download CSV",
                counts_df.to_csv(index=False).encode("utf-8"),
                file_name=f"Counts_{today}.csv"
            )

            if unresolved:
                unresolved_df = pd.DataFrame(unresolved)
                st.warning("Some variables could not be mapped.")
                st.dataframe(unresolved_df)
                st.download_button(
                    "⬇️ Download unresolved report",
                    unresolved_df.to_csv(index=False).encode("utf-8"),
                    file_name="unresolved.csv"
                )

        except Exception as e:
            st.error(f"Failed to generate counts: {e}")

    render_sample_formate_datamap()
