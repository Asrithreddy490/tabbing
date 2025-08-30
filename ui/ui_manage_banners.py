# ui_manage_banners.py
from imports import *


def render_manage_banners_tab():
    st.header("🏷️ Manage Banners (banner.json)")

    # --- Helpers ---
    def _validate_rows(rows):
        ids = set()
        for r in rows:
            if not r.get("id") or not r.get("label"):
                return False, "Each row must have non-empty 'id' and 'label'."
            if r["id"] in ids:
                return False, f"Duplicate id '{r['id']}' found."
            ids.add(r["id"])
        return True, ""

    def _normalize_rows(rows):
        out = []
        for r in rows:
            rid = str(r.get("id", "")).strip()
            lbl = str(r.get("label", "")).strip()
            cond = r.get("condition", None)
            if isinstance(cond, str):
                cond = cond.strip()
                if cond == "":
                    cond = None
            out.append({"id": rid, "label": lbl, "condition": cond})
        return out

    # --- Mode Switch ---
    mode = st.radio("Edit mode", ["Table editor", "Raw JSON"], horizontal=True)
    current_banners = load_banner_config()

    if mode == "Table editor":
        st.write("Add/remove rows directly. Ensure unique `id` values.")

        df = pd.DataFrame(current_banners, columns=["id", "label", "condition"])
        edited = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "id": st.column_config.TextColumn("id", help="Short code (A, B, C...) or custom key"),
                "label": st.column_config.TextColumn("label", help="Display label on banner"),
                "condition": st.column_config.TextColumn(
                    "condition",
                    help="pandas.query condition; leave blank for Total"
                )
            }
        )

        colA, colB, colC, colD = st.columns(4)
        with colA:
            if st.button("💾 Save banners"):
                rows = edited.to_dict(orient="records")
                rows = _normalize_rows(rows)
                ok, msg = _validate_rows(rows)
                if not ok:
                    st.error(f"❌ {msg}")
                else:
                    if save_banner_config(rows):
                        st.success("✅ banner.json saved.")
                        st.rerun()

        with colB:
            if st.button("↩️ Reload from file"):
                st.experimental_rerun()

        with colC:
            if st.button("🧹 Reset to defaults"):
                defaults = get_default_banner_config()
                if save_banner_config(defaults):
                    st.success("✅ Reset to default banners.")
                    st.rerun()

        with colD:
            st.download_button(
                "⬇️ Download banner.json",
                data=json.dumps(_normalize_rows(edited.to_dict(orient="records")), indent=4, ensure_ascii=False),
                file_name="banner.json",
                mime="application/json"
            )

        st.divider()
        st.caption("Tip: Conditions are evaluated via pandas.query on your dataset.")

    else:  # Raw JSON mode
        json_text = st.text_area(
            "banner.json",
            value=json.dumps(current_banners, indent=4, ensure_ascii=False),
            height=400
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("💾 Save JSON"):
                try:
                    parsed = json.loads(json_text)
                    if save_banner_config(parsed):
                        st.success("✅ banner.json saved.")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Invalid JSON: {e}")

        with c2:
            if st.button("🧹 Reset to defaults"):
                defaults = get_default_banner_config()
                if save_banner_config(defaults):
                    st.success("✅ Reset to default banners.")
                    st.rerun()

        with c3:
            uploaded = st.file_uploader("Upload banner.json", type=["json"], label_visibility="collapsed")
            if uploaded is not None:
                try:
                    upl = json.load(uploaded)
                    if save_banner_config(upl):
                        st.success("✅ Uploaded and saved banner.json.")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to load uploaded JSON: {e}")
