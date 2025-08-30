# ui_generate_tables.py
from imports import *
#from core.tab_generator import TabGenerator



def render_generate_tables_tab(questions):
    st.header("📊 Generate Output Tables")

    with st.expander("⚙️ Configuration", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            data_file = st.file_uploader(
                "Upload Data File*",
                type=["csv", "xls", "xlsx"],
                key="generate_tables_data"
            )
        with col2:
            study_name = st.text_input("Study Name*", value=DEFAULT_STUDY_NAME, key="generate_tables_study")
        with col3:
            client_name = st.text_input("Client Name*", value=DEFAULT_CLIENT_NAME, key="generate_tables_client")

    st.subheader("Banner Configuration")
    banner_config = load_banner_config()

    if st.button("✨ Generate Tables", type="primary", disabled=not questions, key="btn_generate_tables"):
        if not all([data_file, study_name, client_name]):
            st.error("Please fill in all required configuration fields (*)")
            st.stop()

        try:
            with st.spinner("⏳ Generating tables..."):
                # Save uploaded file to temp path
                temp_path = f"__generate_tables__{data_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(data_file.getbuffer())

                data = load_data(temp_path)
                month, year = get_now_month_year()
                final_df, file_name = generate_tables(
                    questions=questions,
                    data=data,
                    study_name=study_name,
                    client_name=client_name,
                    banner_config=banner_config,
                    month=month,
                    year=year
                )

                if final_df is not None:
                    st.success(f"✅ Tables generated successfully! Saved to: {file_name}")
                    with open(file_name, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Tables",
                            data=f,
                            file_name=file_name,
                            mime="text/csv",
                            key="btn_download_tables"
                        )
                else:
                    st.warning("No tables were generated")
        except Exception as e:
            st.error(f"❌ Error generating tables: {str(e)}")
            st.exception(e)
