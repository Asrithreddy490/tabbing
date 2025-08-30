from imports import *
from core.utils import clean_blank_and_convert_to_numeric

# ---------- Question storage ----------
def load_questions():
    """Load questions into session state if not already present."""
    if "questions" not in st.session_state:
        st.session_state.questions = []   # start fresh
        st.toast("ℹ️ Starting with an empty question set (session memory).")
    return st.session_state.questions


def save_questions(questions):
    """Save questions into session state only (not to disk)."""
    st.session_state.questions = questions
    st.toast("💾 Questions saved to session memory!")  # Auto hides in ~3s
    return True


def validate_display_structure(structure):
    """Ensure display_structure follows the correct format."""
    if not isinstance(structure, list):
        return False
    for item in structure:
        if not (isinstance(item, (list, tuple)) and len(item) >= 3):
            return False
        if item[0] not in ["code", "net"]:
            return False
    return True


# ---------- Data loading ----------
def load_data(path: str) -> pd.DataFrame:
    """Load data with supported formats and apply cleaning/indexing."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(path)
    elif ext == ".xls":
        df = pd.read_excel(path, engine="xlrd")
    elif ext == ".xlsx":
        df = pd.read_excel(path, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    # Clean but don't force any index
    df = clean_blank_and_convert_to_numeric(df)
    return df


# ---------- Time helpers ----------
def get_now_month_year():
    now = datetime.now()
    return now.strftime("%B"), now.year


# ---------- Raw readers for probe ----------
def try_read_raw(path: str, ext: str):
    """Read a file by extension without pipeline cleaning."""
    try:
        if ext == ".csv":
            df = pd.read_csv(path)
        elif ext == ".xls":
            df = pd.read_excel(path, engine="xlrd")
        elif ext == ".xlsx":
            df = pd.read_excel(path, engine="openpyxl")
        else:
            return (False, None, f"Unsupported file format: {ext}")
        return (True, df, "File read successfully.")
    except ImportError as e:
        return (False, None, f"Missing package: {e}")
    except Exception as e:
        return (False, None, f"Error while reading: {e}")


def probe_file_like(uploaded_file, run_full_pipeline: bool = False):
    """Probe uploaded file (raw + optional pipeline)."""
    name = uploaded_file.name
    ext = os.path.splitext(name)[1].lower()
    temp_path = f"__probe__{name}"

    result = {
        "name": name, "ext": ext, "ok": False, "msg": "",
        "df": None, "pipeline_ok": None, "pipeline_msg": None
    }
    try:
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        ok, df, msg = try_read_raw(temp_path, ext)
        result.update({"ok": ok, "df": df, "msg": msg})

        if ok and run_full_pipeline:
            try:
                full_df = load_data(temp_path)
                result["pipeline_ok"] = True
                result["pipeline_msg"] = f"Full pipeline succeeded. Shape: {full_df.shape}"
                st.toast("✅ Full pipeline check passed!")
            except Exception as e:
                result["pipeline_ok"] = False
                result["pipeline_msg"] = f"Full pipeline failed: {e}"
                st.toast("❌ Full pipeline check failed!")
    finally:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass

    return result
