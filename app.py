# app.py
"""
Farm Waste -> Fertilizer Advisor (Enhanced AI version)
Features:
 - Free-text fuzzy matching for waste names (rapidfuzz)
 - Dataset (waste_data.csv) editable and used for suggestions
 - Easy to deploy on Streamlit Cloud (online)
Run: pip install -r requirements.txt
     streamlit run app.py
"""

import streamlit as st
import pandas as pd
import os
from rapidfuzz import process, fuzz
from datetime import datetime

DATA_CSV = "waste_data.csv"
st.set_page_config(page_title="Farm Waste → Fertilizer Advisor", page_icon="🌾", layout="centered")

st.title("🌾 Farm Waste → Fertilizer Advisor (Enhanced)")
st.write("Type any waste (e.g., 'cow manure', 'banana peels') or choose from the list. The app uses fuzzy matching to find the best recommendation.")

@st.cache_data
def load_dataset(path=DATA_CSV):
    if not os.path.exists(path):
        st.error(f"Dataset not found: {path}")
        return pd.DataFrame()
    return pd.read_csv(path)

df = load_dataset()
if df.empty:
    st.stop()

waste_list = list(df["Waste Type"].values)

# Input area
st.header("Input")
col1, col2 = st.columns([3,1])
with col1:
    user_text = st.text_input("Enter waste type (free text):", placeholder="e.g., 'cow manure', 'banana peels'")
    qty = st.number_input("Quantity (kg) — optional (for yield estimate):", min_value=0.0, step=0.1, format="%.2f")
with col2:
    st.write("Or pick from list:")
    selected = st.selectbox("", options=[""] + waste_list)

# Matching
def find_best_match(user_input, choices, score_cutoff=50):
    res = process.extractOne(user_input, choices, scorer=fuzz.WRatio)
    if res:
        match, score, _ = res
        if score >= score_cutoff:
            return match, score
        else:
            return None, score
    return None, 0

matched_type = None
match_score = None
if selected:
    matched_type = selected
    match_score = 100
elif user_text.strip():
    mt, score = find_best_match(user_text.strip(), waste_list)
    if mt:
        matched_type = mt
        match_score = score
    else:
        match_score = score

st.header("Recommendation")
if matched_type:
    waste_row = df[df["Waste Type"] == matched_type].iloc[0].to_dict()
    st.subheader(f"✅ Matched Waste Type: {matched_type}  (score {match_score})")
    st.markdown(f"**Best Use:** {waste_row.get('Best Use','-')}  ")
    st.markdown(f"**Compost Time:** {waste_row.get('Compost Time','-')}  ")
    st.markdown(f"**Nutrient Type:** {waste_row.get('Nutrient','-')}  ")
    st.markdown(f"**Tips:** {waste_row.get('Tips','-')}")

    # Estimate compost output
    est_compost = None
    if qty and qty > 0:
        # Try to get a yield percentage from dataset if available; otherwise use 40%
        yp = waste_row.get('Yield_pct', None)
        try:
            yield_pct = float(yp) if yp is not None else 40.0
        except:
            yield_pct = 40.0
        est_compost = qty * (yield_pct / 100.0)
        st.info(f"Estimated compost output from {qty:.2f} kg input: **{est_compost:.2f} kg** (approx; yield {yield_pct}%).")
        st.caption("Note: yield is a rough approximation; actual output depends on moisture and method.")

    # Downloadable text report
    def format_report(wt_row, qty=None, est=None):
        lines = []
        lines.append("Farm Waste → Fertilizer Advisor Report")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append(f"Waste Type: {wt_row.get('Waste Type','')}")
        lines.append(f"Best Use: {wt_row.get('Best Use','')}")
        lines.append(f"Compost Time: {wt_row.get('Compost Time','')}")
        lines.append(f"Nutrient: {wt_row.get('Nutrient','')}")
        lines.append(f"Tips: {wt_row.get('Tips','')}")
        if qty and est:
            lines.append("")
            lines.append(f"Input Quantity: {qty:.2f} kg")
            lines.append(f"Estimated Compost Output: {est:.2f} kg")
        return "\\n".join(lines)

    report_text = format_report(waste_row, qty if qty>0 else None, est_compost if est_compost else None)
    st.download_button("Download advice report (TXT)", data=report_text, file_name=f"fert_advice_{matched_type.replace(' ','_')}.txt")

else:
    if user_text.strip() == "":
        st.info("Type a waste name above to get a recommendation or select from the list.")
    else:
        st.warning("No confident match found. Try rephrasing or choose from the list.")
        suggestions = process.extract(user_text.strip(), waste_list, scorer=fuzz.WRatio, limit=5)
        if suggestions:
            st.markdown("**Top suggestions:**")
            for s in suggestions:
                st.write(f"- {s[0]} (score {s[1]})")

# Dataset editor (optional) - simple add
st.header("Dataset (view & add)")
with st.expander("Current waste data"):
    st.dataframe(df)

with st.expander("Add a new waste type"):
    new_waste = st.text_input("Waste Type name")
    new_best_use = st.text_input("Best Use")
    new_compost = st.text_input("Compost Time")
    new_nutrient = st.text_input("Nutrient Type")
    new_tips = st.text_area("Tips / Notes")
    new_yield = st.text_input("Estimated yield % (optional)")
    if st.button("Add new waste type"):
        if not new_waste.strip():
            st.error("Enter a waste type name.")
        else:
            new_row = {
                "Waste Type": new_waste.strip(),
                "Best Use": new_best_use.strip(),
                "Compost Time": new_compost.strip(),
                "Nutrient": new_nutrient.strip(),
                "Tips": new_tips.strip()
            }
            if new_yield.strip():
                try:
                    new_row["Yield_pct"] = float(new_yield.strip())
                except:
                    pass
            df = df.append(new_row, ignore_index=True)
            df.to_csv(DATA_CSV, index=False)
            st.success(f"Added '{new_waste.strip()}' to dataset and saved to {DATA_CSV}. Refresh page to see changes.")
