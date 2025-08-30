# ui/ui_import_questions.py
from imports import *
from ui.ui_file_formate import render_sample_formate_datamap


def render_import_questions_tab(questions):
    st.subheader("📥 Import Questions")

    datamap_file = st.file_uploader(
        "Upload Datamap Excel File", 
        type=["xls", "xlsx", "xlsm"], 
        key="import_dm"
    )
    data_file_for_axis = st.file_uploader(
        "Upload Data File (for axis resolution)", 
        type=["csv", "xls", "xlsx"], 
        key="import_data"
    )

    if datamap_file and st.button("⚡ Generate Questions from Datamap", type="primary", key="btn_import_questions"):
        try:
            with st.spinner("🔍 Processing datamap..."):
                data_df_axis = None
                if data_file_for_axis:
                    data_temp_path = save_uploaded_file(data_file_for_axis, "axis")
                    data_df_axis = load_data(data_temp_path)

                dm_temp_path = save_uploaded_file(datamap_file, "datamap")
                new_questions = parse_datamap_to_json(dm_temp_path, data_df=data_df_axis)

                existing_ids = [q['id'] for q in questions] if questions else [0]
                start_id = max(existing_ids) + 1
                for i, q in enumerate(new_questions):
                    q['id'] = start_id + i

                questions.extend(new_questions)
                if save_questions(questions):
                    st.success(f"✅ Added {len(new_questions)} new questions from datamap!")
                    st.json(new_questions[:3])
                    st.rerun()
        except Exception as e:
            st.error(f"❌ Error processing datamap: {e}")
    
    render_sample_formate_datamap()
