# 🥗 Healthy Snack & Energy Habits Survey

A Streamlit-based psychological state survey for WIUT Fundamentals of Programming coursework.

## Files
- `app.py` — Main Streamlit application
- `questions.json` — External questions file (loaded at runtime)
- `requirements.txt` — Python dependencies

## Run Locally
```bash
pip install streamlit
streamlit run app.py
```

## Deploy to Streamlit Cloud (Free Hosting)
1. Push all files to a **public GitHub repository**
2. Go to https://share.streamlit.io
3. Sign in with GitHub
4. Click **"New app"** → select your repo → set `app.py` as the main file
5. Click **Deploy** — your app will be live at a public URL

## CW Checklist
- [x] 15 original questions loaded from external JSON file
- [x] 3–5 answer options per question with custom scores
- [x] 5 psychological state outputs based on score
- [x] Name validation (letters, hyphens, apostrophes, spaces only)
- [x] DOB validation (YYYY-MM-DD with logical checks)
- [x] Student ID validation (digits only)
- [x] Save results as TXT, CSV, or JSON
- [x] Load existing results from file
- [x] Uses all 10 variable types: int, str, float, list, tuple, range, bool, dict, set, frozenset
- [x] for loop + range for validation
- [x] while loop for validation
- [x] if / elif / else conditionals
- [x] 6+ user-defined functions
- [x] Web-based interface (Streamlit)
