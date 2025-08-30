# ui/ui_add_edit_questions.py
from imports import *



def render_add_edit_questions_tab():
    st.subheader("✏️ Add/Edit Questions")

    form_defaults = {
        "question_var": "",
        "question_text": "",
        "base_text": "Total Respondents",
        "display_structure": [
            ["code", "Male", 1],
            ["code", "Female", 2],
            ["net", "All Genders", [1, 2]]
        ],
        "base_filter": "",
        "question_type": "single",
        "mean_var": "",
        "show_sigma": True
    }

    # Prefill if editing
    if "edit_id" in st.session_state:
        q_to_edit = next((q for q in st.session_state.questions if q['id'] == st.session_state.edit_id), None)
        if q_to_edit:
            form_defaults.update({
                "question_var": ",".join(q_to_edit['question_var']) if isinstance(q_to_edit['question_var'], list) else q_to_edit['question_var'],
                "question_text": q_to_edit['question_text'],
                "base_text": q_to_edit['base_text'],
                "display_structure": q_to_edit['display_structure'],
                "base_filter": q_to_edit['base_filter'] or "",
                "question_type": q_to_edit['question_type'],
                "mean_var": q_to_edit['mean_var'] or "",
                "show_sigma": q_to_edit.get("show_sigma", True)
            })
        else:
            st.warning("Question not found for editing.")
            st.session_state.pop("edit_id", None)

    # Form UI
    with st.form("question_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            question_var = st.text_input("Question Variable*", value=form_defaults["question_var"], key="q_var")
            question_text = st.text_input("Question Text*", value=form_defaults["question_text"], key="q_text")
            base_text = st.text_input("Base Text*", value=form_defaults["base_text"], key="q_base_text")
            question_type = st.selectbox(
                "Question Type*", ["single", "multi", "open_numeric"],
                index=["single", "multi", "open_numeric"].index(form_defaults["question_type"]),
                key="q_type"
            )
        with col2:
            display_structure = st.text_area(
                "Display Structure (JSON)*",
                value=json.dumps(form_defaults["display_structure"], indent=2),
                height=500,
                key="q_display_structure"
            )
            base_filter = st.text_input("Base Filter", value=form_defaults["base_filter"], key="q_base_filter")
            mean_var = st.text_input("Mean Variable", value=form_defaults["mean_var"], key="q_mean_var")
            show_sigma = st.checkbox("Show Sigma", value=form_defaults["show_sigma"], key="q_show_sigma")

        submitted = st.form_submit_button("💾 Save Question", type="primary")

        if submitted:
            try:
                display_structure_parsed = json.loads(display_structure)
                if not validate_display_structure(display_structure_parsed):
                    st.error("Invalid display structure format")
                    st.stop()
            except json.JSONDecodeError:
                st.error("Display Structure must be valid JSON")
                st.stop()

            question_data = {
                "question_var": [v.strip() for v in question_var.split(",")] if "," in question_var else question_var,
                "question_text": question_text,
                "base_text": base_text,
                "display_structure": display_structure_parsed,
                "base_filter": base_filter if base_filter else None,
                "question_type": question_type,
                "mean_var": mean_var if mean_var else None,
                "show_sigma": show_sigma
            }

            if "edit_id" in st.session_state:
                for q in st.session_state.questions:
                    if q['id'] == st.session_state.edit_id:
                        q.update(question_data)
                        break
                success_msg = f"Question ID {st.session_state.edit_id} updated!"
                st.session_state.pop("edit_id", None)
            else:
                new_id = max([q['id'] for q in st.session_state.questions], default=0) + 1
                question_data["id"] = new_id
                st.session_state.questions.append(question_data)
                success_msg = f"Question saved with ID {new_id}!"

            if save_questions(st.session_state.questions):
                st.success(success_msg)
                st.rerun()

    # Show current questions
    with st.expander("📋 View Current Questions (JSON)"):
        st.json(st.session_state.questions)
