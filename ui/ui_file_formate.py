from imports import *

def render_sample_formats(key_suffix="default"):
    with st.expander("📄 Sample Formats: Datamap & Tabplan", expanded=False):
        st.caption("Here are sample formats so you know how to prepare your files:")

        choice = st.radio(
            "Select format to preview:",
            ["🗂️ Datamap Format", "📑 Tabplan Format"],
            index=0,
            horizontal=True,
            key=f"radio_sample_formats_{key_suffix}"   # 🔑 unique key
        )

        if choice == "🗂️ Datamap Format":
            st.image("assets/Sample_Datamap.png", caption="Example Datamap Excel", use_container_width=True)
        else:
            st.image("assets/Sample_Tabplan.png", caption="Example Tabplan Excel", use_container_width=True)



def render_sample_formate_datamap():
    
    with st.expander("📄 Sample Formats: Datamap", expanded=False):
        st.caption("Here are sample format so you know how to prepare your file:")

        # Datamap Format (open by default)
        with st.expander("🗂️ Datamap Format", expanded=True):
            st.image("assets/Sample_Datamap.png", caption="Example Datamap Excel", use_container_width=True)

        