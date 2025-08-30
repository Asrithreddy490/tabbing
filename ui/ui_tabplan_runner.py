from imports import *
from ui.ui_file_formate import render_sample_formats


def render_tabplan_runner_tab():
    st.subheader("🗂️ Tabplan Runner")

    tabplan_file = st.file_uploader("Upload Tabplan Excel", type=["xls", "xlsx"], key="tabplan_file")
    datamap_for_tabplan = st.file_uploader("Upload Datamap (for auto-create)", type=["xls", "xlsx", "xlsm"], key="tabplan_dm")
    data_file_tabplan = st.file_uploader("Upload Data File", type=["csv", "xls", "xlsx"], key="tabplan_data")

    if tabplan_file and st.button("🔍 Parse Tabplan", key="parse_tabplan_btn"):
        try:
            tp_temp_path = save_uploaded_file(tabplan_file, "tabplan")
            tab_items = parse_tabplan(tp_temp_path)
            if not tab_items:
                st.warning("No questions detected in the tabplan.")
            else:
                st.success(f"Detected {len(tab_items)} questions.")
            st.session_state["_tabplan_items"] = tab_items
            st.rerun()  # 🔥 refresh immediately after parsing
        except Exception as e:
            st.error(f"Failed to read tabplan: {e}")

    tab_items = st.session_state.get("_tabplan_items", [])
    if tab_items and data_file_tabplan:
        data_temp_path = save_uploaded_file(data_file_tabplan, "tabplan_data")
        data_df_for_run = load_data(data_temp_path)

        # --- Auto-create missing questions from datamap ---
        if datamap_for_tabplan is not None and st.button("📎 Auto-create missing questions from Datamap", key="btn_auto_create"):
            try:
                dm_temp_path = save_uploaded_file(datamap_for_tabplan, "tabplan_dm")
                all_from_dm = parse_datamap_to_json(dm_temp_path, data_df=data_df_for_run)

                created = []
                for item in tab_items:
                    qid = str(item["qid"]).lower()
                    if not any(qid in str(q.get("question_var")).lower() for q in st.session_state.questions):
                        match = next((q for q in all_from_dm if str(q.get("question_var")).lower() == qid), None)
                        if match:
                            new_id = max([q['id'] for q in st.session_state.questions], default=0) + 1
                            match["id"] = new_id
                            st.session_state.questions.append(match)
                            created.append(qid)

                if created:
                    save_questions(st.session_state.questions)
                    st.success(f"✅ Created {len(created)} missing questions from datamap.")
                    st.rerun()  # 🔥 refresh immediately after creating
                else:
                    st.info("No new questions created — all questions already exist.")
            except Exception as e:
                st.error(f"Auto-create failed: {e}")

        # --- Render tabs for tabplan questions ---
        tab_labels = [f"{i+1}. {item['qid']}" for i, item in enumerate(tab_items)]
        tabs = st.tabs(tab_labels)
        export_sheets: dict[str, pd.DataFrame] = {}

        # --- Improved Matching Logic ---
        def normalize(s: str) -> str:
            if not s:
                return ""
            return re.sub(r"[^a-z0-9_]+", "", str(s).strip().lower())

        def find_question_config(qid, label):
            qid_norm = normalize(qid)
            token_norm = normalize(label.split(":", 1)[0])

            for q in st.session_state.questions or []:
                qv = q.get("question_var")

                # normalize everything for comparison
                if isinstance(qv, str):
                    if normalize(qv) == qid_norm or normalize(qv) == token_norm:
                        return q
                elif isinstance(qv, list):
                    if any(normalize(v) == qid_norm or normalize(v) == token_norm for v in qv):
                        return q

                # fallback: fuzzy match in question text
                qtext = str(q.get("question_text", "")).lower()
                if qid_norm in qtext or token_norm in qtext:
                    return q

            return None

        for (item, t) in zip(tab_items, tabs):
            with t:
                qid, qlabel = item["qid"], item["label"]
                st.subheader(qid)
                st.caption(qlabel)
                qcfg = find_question_config(qid, qlabel)
                if qcfg is None:
                    st.warning("No matching saved question config found. Try using Auto-create above.")
                    continue

                if st.button(f"📊 Generate table for {qid}", key=f"btn_{qid}"):
                    try:
                        with st.spinner("Generating table..."):
                            month, year = get_now_month_year()
                            df_out, out_file = generate_tables(
                                questions=[qcfg],
                                data=data_df_for_run,
                                study_name=DEFAULT_STUDY_NAME,
                                client_name=DEFAULT_CLIENT_NAME,
                                banner_config=load_banner_config(),
                                month=month,
                                year=year
                            )
                            if df_out is not None:
                                st.dataframe(df_out.head(50))
                                export_sheets[qid] = df_out
                                with open(out_file, "rb") as f:
                                    st.download_button(f"⬇️ Download CSV for {qid}", f, file_name=out_file)
                    except Exception as e:
                        st.error(f"Failed to generate: {e}")

    # Show sample images
    render_sample_formats("tabplan")
