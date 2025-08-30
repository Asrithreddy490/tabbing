from imports import *


# ----------------------
# Page + session
# ----------------------
set_page()
if 'questions' not in st.session_state:
    st.session_state.questions = load_questions()

# ----------------------
# Helper: show/hide sidebar
# ----------------------
def _toggle_sidebar(show: bool):
    if show:
        st.markdown("<style>section[data-testid='stSidebar']{display:block !important;}</style>", unsafe_allow_html=True)
    else:
        st.markdown("<style>section[data-testid='stSidebar']{display:none !important;}</style>", unsafe_allow_html=True)

# ----------------------
# Navigation
# ----------------------
SECTIONS = [
    "🧪 File Format Checker",
    "⚙️ Processing",
    "🏷️ Manage Banners",
    "📊 Generate Tables",
    
]

section = st.radio("Navigate", SECTIONS, horizontal=True, key="section_switcher")

# Sidebar only in Processing
_toggle_sidebar(section == "⚙️ Processing")

# ----------------------
# Sidebar: Stored Questions
# ----------------------
if section == "⚙️ Processing":
    render_stored_questions_sidebar()

# ----------------------
# File Format Checker
# ----------------------
if section == "🧪 File Format Checker":
    render_file_checker_tab()

# ----------------------
# Section: Manage Banners
# ----------------------
elif section == "🏷️ Manage Banners":
    render_manage_banners_tab()

# ----------------------
# Section: Generate Tables
# ----------------------
elif section == "📊 Generate Tables":
    render_generate_tables_tab(st.session_state.questions)

# ----------------------
# Processing Tab (4 subtabs)
# ----------------------
elif section == "⚙️ Processing":
    st.header("⚙️ Processing")
    sub_tabs = st.tabs(["📥 Import Questions", "🗂️ Tabplan Runner", "✏️ Add/Edit Questions", "🔢 Generate Counts"])

    # ----------------------
    # Import Questions
    # ----------------------
    with sub_tabs[0]:
        render_import_questions_tab(st.session_state.questions)


    # ----------------------
    # Tabplan Runner
    # ----------------------
     # --- Tabplan Runner ---
    with sub_tabs[1]:
        render_tabplan_runner_tab()


    # ----------------------
    # Add/Edit Questions
    # ----------------------
    with sub_tabs[2]:
        render_add_edit_questions_tab()
            

    # ----------------------
    # Generate Counts
    # ----------------------
    with sub_tabs[3]:
        render_generate_counts_tab()
    
    
    
    
