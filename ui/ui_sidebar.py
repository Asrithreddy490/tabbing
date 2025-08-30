# ui_sidebar.py
from imports import *

def render_stored_questions_sidebar():
    st.sidebar.header("🔍 Stored Questions")
    # --- Export/Import Session Questions ---
    with st.sidebar.expander("⚙️ Session Data"):
        # Export Questions
        if st.session_state.get("questions"):
            q_json = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
            st.download_button(
                "⬇️ Export Questions JSON",
                q_json.encode("utf-8"),
                file_name="questions_session.json",
                mime="application/json",
                key="btn_export_questions"
            )

        # Import Questions
        uploaded_q = st.file_uploader("⬆️ Import Questions JSON", type=["json"], key="upload_questions_json")
        if uploaded_q is not None:
            try:
                data = json.load(uploaded_q)
                if isinstance(data, list):
                    st.session_state.questions = data
                    st.toast("✅ Imported questions into session memory!")
                    st.rerun()
                else:
                    st.error("❌ Invalid format: Must be a list of questions.")
            except Exception as e:
                st.error(f"❌ Failed to import questions: {e}")



    if st.session_state.questions:
        # Build mapping of labels → IDs
        question_options = {
            f"ID {q['id']} - {q['question_text'][:30]}...": q['id']
            for q in st.session_state.questions
        }

        selected_label = st.sidebar.selectbox(
            "Select Question",
            list(question_options.keys()),
            key="question_select"
        )
        selected_id = question_options[selected_label]

        # --- Vertical action buttons ---
        if st.sidebar.button("✏️ Edit Question", key="edit_btn"):
            st.session_state.edit_id = selected_id
            st.rerun()

        if st.sidebar.button("🗑️ Delete Selected", key="delete_btn"):
            st.session_state.questions = [
                q for q in st.session_state.questions if q['id'] != selected_id
            ]
            st.toast(f"🗑️ Deleted question ID {selected_id}")
            st.rerun()

        if st.sidebar.button("🧹 Delete All Questions", key="delete_all_btn"):
            st.session_state.questions = []
            st.toast("🧹 Cleared all questions from session memory")
            st.rerun()

       

    else:
        st.sidebar.info("ℹ️ No questions stored yet. Import or add new questions below.")
