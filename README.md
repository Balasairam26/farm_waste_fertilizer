# Farm Waste → Fertilizer Advisor (Enhanced AI version)

This is an online-ready Streamlit app that helps farmers convert farm waste into useful fertilizers.
The app supports free-text input (fuzzy matching) to recognize waste types like "cow manure" or "banana peels".

## Files
- `app.py` - Main Streamlit app.
- `waste_data.csv` - Dataset of waste types and recommendations.
- `requirements.txt` - Python dependencies.

## Deploy to Streamlit Cloud (online)
1. Create a new GitHub repository and push these files.
2. Go to https://share.streamlit.io and connect your GitHub account.
3. Choose the repository and branch, then deploy. Streamlit Cloud will install dependencies from `requirements.txt` and run `app.py`.

## Run locally (optional)
```bash
pip install -r requirements.txt
streamlit run app.py
```

Developed for quick hackathon demos.
