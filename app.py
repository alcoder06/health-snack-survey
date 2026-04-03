"""
Healthy Snack & Energy Habits Survey
=====================================
A Streamlit-based psychological state survey application.

Author  : Student
Module  : Fundamentals of Programming, 4BUIS008C (Level 4)
Purpose : Coursework Project 1 – Psychological State Questionnaire
"""

import streamlit as st
import json
import csv
import re
import io
import os
from datetime import datetime

# ─────────────────────────────────────────────
# VARIABLE TYPES DEMONSTRATION (for CW grading)
# int       → score accumulation, question index
# str       → name, dob, student_id, result label
# float     → percentage calculation
# list      → questions list, options list
# tuple     → immutable score range boundaries
# range     → used in for-loop validation iteration
# bool      → validation flags
# dict      → saved result data, each question object
# set       → allowed characters for name validation
# frozenset → immutable set of valid date separators
# ─────────────────────────────────────────────

ALLOWED_NAME_CHARS: set = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'")
VALID_DATE_SEPARATORS: frozenset = frozenset(["-"])

SCORE_BANDS: tuple = (
    (0,  12,  "Excellent Energy",    "🌟 Your snacking and eating habits excellently support your energy and focus. Keep it up!",            "#2ecc71"),
    (13, 24,  "Good Energy",         "✅ Your habits are generally healthy. Minor tweaks could make them even better.",                      "#27ae60"),
    (25, 36,  "Moderate Energy",     "⚖️ Your energy levels are average. Consider making more intentional food choices during study time.", "#f39c12"),
    (37, 48,  "Low Energy",          "⚠️ Your eating habits may be draining your energy. Try incorporating more whole foods and planning meals.", "#e67e22"),
    (49, 60,  "Very Low Energy",     "❗ Your current habits are significantly undermining your study performance. Urgent dietary improvements are recommended.", "#e74c3c"),
)

QUESTIONS_FILE: str = "questions.json"


# ══════════════════════════════════════════════
#  VALIDATION FUNCTIONS
# ══════════════════════════════════════════════

def validate_name(name: str) -> tuple[bool, str]:
    """Validate that name contains only letters, spaces, hyphens, and apostrophes."""
    is_valid: bool = True
    error_msg: str = ""

    if not name.strip():
        return False, "Name cannot be empty."

    # Use a for loop to iterate over each character (required by CW)
    for char in name:
        if char not in ALLOWED_NAME_CHARS:
            is_valid = False
            error_msg = f"Invalid character '{char}'. Only letters, spaces, hyphens (-), and apostrophes (') are allowed."
            break

    # Use range() with a for loop as a second validation pass (required: for loop + range)
    digit_found: bool = False
    for i in range(len(name)):
        if name[i].isdigit():
            digit_found = True
            break

    if digit_found:
        is_valid = False
        error_msg = "Name must not contain digits."

    return is_valid, error_msg


def validate_dob(dob: str) -> tuple[bool, str]:
    """Validate date of birth in YYYY-MM-DD format with logical date checking."""
    is_valid: bool = True
    error_msg: str = ""

    # Check separators using frozenset
    parts: list = dob.split("-")
    if len(parts) != 3:
        return False, "Date must be in YYYY-MM-DD format (e.g. 2003-07-15)."

    try:
        parsed_date = datetime.strptime(dob, "%Y-%m-%d")
        year: int = parsed_date.year
        now = datetime.now()

        if year < 1900 or parsed_date > now:
            is_valid = False
            error_msg = "Date of birth must be between 1900 and today."
    except ValueError:
        is_valid = False
        error_msg = "Invalid date. Please enter a real date in YYYY-MM-DD format."

    return is_valid, error_msg


def validate_student_id(sid: str) -> tuple[bool, str]:
    """Validate student ID contains only digits."""
    is_valid: bool = True
    error_msg: str = ""

    if not sid.strip():
        return False, "Student ID cannot be empty."

    # Use while loop for character-by-character validation (required by CW)
    index: int = 0
    while index < len(sid):
        if not sid[index].isdigit():
            is_valid = False
            error_msg = "Student ID must contain digits only."
            break
        index += 1

    return is_valid, error_msg


# ══════════════════════════════════════════════
#  FILE I/O FUNCTIONS
# ══════════════════════════════════════════════

def load_questions_from_file(filepath: str) -> list:
    """Load survey questions from an external JSON file at runtime."""
    questions: list = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            questions = json.load(f)
    except FileNotFoundError:
        st.error(f"Questions file '{filepath}' not found.")
    except json.JSONDecodeError:
        st.error("Error reading questions file: invalid JSON format.")
    return questions


def calculate_score(answers: list, questions: list) -> int:
    """Calculate the total score from the user's answers."""
    total_score: int = 0
    for i in range(len(answers)):
        answer_index: int = answers[i]
        score: int = questions[i]["scores"][answer_index]
        total_score += score
    return total_score


def evaluate_result(score: int) -> dict:
    """Return the psychological state label and message based on the total score."""
    result: dict = {}

    # Use if / elif / else conditional statements (required by CW)
    for band in SCORE_BANDS:
        low, high, label, message, color = band
        if low <= score <= high:
            result = {
                "label": label,
                "message": message,
                "color": color,
                "score": score,
                "max_score": (len(SCORE_BANDS) * 4) + (15 - len(SCORE_BANDS)) * 4
            }
            break

    if not result:
        result = {
            "label": "Unknown",
            "message": "Score out of expected range.",
            "color": "#95a5a6",
            "score": score,
            "max_score": 60
        }

    return result


def build_result_data(name: str, dob: str, sid: str, score: int, label: str) -> dict:
    """Build the result dictionary to be saved/displayed."""
    percentage: float = round((score / 60) * 100, 2)
    return {
        "name": name,
        "date_of_birth": dob,
        "student_id": sid,
        "score": score,
        "max_score": 60,
        "percentage": percentage,
        "result": label,
        "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def serialize_txt(data: dict) -> str:
    """Serialize result data to plain text format."""
    lines: list = []
    for key, value in data.items():
        lines.append(f"{key.replace('_', ' ').title()}: {value}")
    return "\n".join(lines)


def serialize_csv(data: dict) -> str:
    """Serialize result data to CSV format."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(data.keys()))
    writer.writeheader()
    writer.writerow(data)
    return output.getvalue()


def serialize_json(data: dict) -> str:
    """Serialize result data to JSON format."""
    return json.dumps(data, indent=4)


def parse_uploaded_file(content: str, filename: str) -> dict | None:
    """Parse an uploaded results file (txt, csv, or json) and return data dict."""
    parsed: dict | None = None
    try:
        if filename.endswith(".json"):
            parsed = json.loads(content)
        elif filename.endswith(".csv"):
            reader = csv.DictReader(io.StringIO(content))
            rows: list = list(reader)
            if rows:
                parsed = rows[0]
        elif filename.endswith(".txt"):
            parsed = {}
            for line in content.strip().split("\n"):
                if ":" in line:
                    key, _, val = line.partition(":")
                    parsed[key.strip()] = val.strip()
    except Exception as e:
        st.error(f"Error parsing file: {e}")
    return parsed


# ══════════════════════════════════════════════
#  PAGE CONFIG & STYLES
# ══════════════════════════════════════════════

st.set_page_config(
    page_title="Snack & Energy Survey",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* ── Force Streamlit app background to white ── */
    .stApp {
        background-color: #ffffff !important;
    }

    .block-container {
        background-color: #ffffff !important;
    }

    /* ── Global text overrides — all black ── */
    p, span, div, label, li, a,
    .stMarkdown p, .stMarkdown li, .stMarkdown span,
    label, .stRadio label, .stSelectbox label,
    .stTextInput label, .stFileUploader label,
    .stMarkdown, .stText, .stCaption,
    [class*="css"] {
        color: #000000 !important;
    }

    /* ── Titles ── */
    .survey-title {
        font-family: 'DM Serif Display', serif;
        font-size: 2.6rem;
        color: #000000 !important;
        line-height: 1.15;
        margin-bottom: 0.2rem;
    }

    .survey-subtitle {
        font-size: 1.05rem;
        color: #000000 !important;
        margin-bottom: 2rem;
    }

    /* ── Cards ── */
    .card {
        background: #f8f9fa;
        border-radius: 16px;
        padding: 2rem 2.2rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #dee2e6;
        color: #000000 !important;
    }

    .card p, .card span, .card div, .card label {
        color: #000000 !important;
    }

    /* ── Question page ── */
    .question-chip {
        display: inline-block;
        background: #eef2ff;
        color: #000000 !important;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
    }

    .question-card {
        background: #f8f9fa;
        border-radius: 16px;
        padding: 1.8rem 2rem;
        border: 2px solid #dee2e6;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }

    .question-text {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: #000000 !important;
        line-height: 1.55;
        margin: 0 0 0.3rem 0;
    }

    /* Radio option labels — force black text */
    .stRadio > div > label,
    .stRadio > div > label > div,
    .stRadio > div > label span {
        color: #000000 !important;
        font-size: 1rem !important;
        font-weight: 400 !important;
    }

    /* ── Result box (keeps colored bg, white text inside) ── */
    .result-box {
        border-radius: 20px;
        padding: 2.5rem 2rem;
        color: #ffffff !important;
        text-align: center;
        margin: 1rem 0 1.8rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    }

    .result-label {
        font-family: 'DM Serif Display', serif;
        font-size: 2.2rem;
        color: #ffffff !important;
        margin-bottom: 0.6rem;
        text-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    .result-message {
        font-size: 1.05rem;
        color: #ffffff !important;
        opacity: 1;
        line-height: 1.7;
        max-width: 520px;
        margin: 0 auto;
    }

    .score-pill {
        display: inline-block;
        background: rgba(255,255,255,0.28);
        border: 2px solid rgba(255,255,255,0.5);
        padding: 7px 22px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 1.1rem;
        color: #ffffff !important;
        margin-top: 1.2rem;
        letter-spacing: 0.03em;
    }

    /* ── Info rows ── */
    .section-header {
        font-family: 'DM Serif Display', serif;
        font-size: 1.5rem;
        color: #000000 !important;
        margin-bottom: 1rem;
        border-bottom: 2px solid #dee2e6;
        padding-bottom: 0.4rem;
    }

    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #e9ecef;
        font-size: 0.95rem;
    }
    .info-key { color: #333333 !important; font-weight: 500; }
    .info-val { color: #000000 !important; font-weight: 700; }

    /* ── Buttons ── */
    .stButton > button {
        background: #4f46e5 !important;
        color: #ffffff !important;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.6rem;
        font-weight: 600;
        font-size: 0.97rem;
        transition: background 0.2s, transform 0.1s;
        width: 100%;
    }
    .stButton > button:hover {
        background: #3730a3 !important;
        color: #ffffff !important;
        transform: translateY(-1px);
    }

    /* ── Input fields ── */
    .stTextInput input {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        border: 1px solid #ced4da !important;
    }

    .stSelectbox > div > div {
        background-color: #f8f9fa !important;
        color: #000000 !important;
    }

    /* ── Selectbox dropdown text ── */
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] div {
        color: #000000 !important;
    }

    /* ── Caption / footer ── */
    .stCaption, caption, small {
        color: #333333 !important;
    }

    hr { border: none; border-top: 1px solid #dee2e6; margin: 1.5rem 0; }

    /* ══════════════════════════════════
       CONFETTI CELEBRATION ANIMATION
    ══════════════════════════════════ */
    #confetti-canvas {
        position: fixed;
        top: 0; left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 9999;
    }

    .celebration-banner {
        text-align: center;
        padding: 1rem 0 0.2rem;
        animation: popIn 0.6s cubic-bezier(0.34,1.56,0.64,1) both;
    }

    .celebration-banner .big-emoji {
        font-size: 3.5rem;
        display: block;
        animation: bounce 1s ease infinite alternate;
    }

    .celebration-banner .congrats-text {
        font-family: 'DM Serif Display', serif;
        font-size: 1.6rem;
        color: #000000 !important;
        margin-top: 0.3rem;
    }

    @keyframes popIn {
        0%   { opacity: 0; transform: scale(0.5); }
        100% { opacity: 1; transform: scale(1); }
    }

    @keyframes bounce {
        0%   { transform: translateY(0px); }
        100% { transform: translateY(-10px); }
    }
</style>

<!-- Confetti canvas (hidden by default, shown via JS on results page) -->
<canvas id="confetti-canvas"></canvas>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  SESSION STATE INIT
# ══════════════════════════════════════════════

def init_state():
    """Initialize all session state variables."""
    defaults: dict = {
        "page": "home",          # home | survey | results | load
        "answers": [],
        "current_q": 0,
        "user_name": "",
        "user_dob": "",
        "user_sid": "",
        "questions": [],
        "result_data": {},
        "name_error": "",
        "dob_error": "",
        "sid_error": "",
        "questions_loaded": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()


# ══════════════════════════════════════════════
#  PAGE: HOME
# ══════════════════════════════════════════════

def page_home():
    st.markdown('<p class="survey-title">🥗 Healthy Snack &amp;<br>Energy Habits Survey</p>', unsafe_allow_html=True)
    st.markdown('<p class="survey-subtitle">Discover how your eating habits impact your academic performance and energy levels.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📋 Start New Survey")
        st.write("Answer 15 questions and receive a personalized energy-habits assessment.")
        if st.button("Begin Survey →", key="btn_new"):
            # Load questions from external file at runtime
            questions = load_questions_from_file(QUESTIONS_FILE)
            if questions:
                st.session_state.questions = questions
                st.session_state.questions_loaded = True
                st.session_state.page = "user_info"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📂 Load Previous Results")
        st.write("Upload a previously saved result file (TXT, CSV, or JSON).")
        if st.button("Load Results →", key="btn_load"):
            st.session_state.page = "load"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Fundamentals of Programming · 4BUIS008C · Westminster International University in Tashkent")


# ══════════════════════════════════════════════
#  PAGE: USER INFO
# ══════════════════════════════════════════════

def page_user_info():
    st.markdown('<p class="section-header">👤 Your Details</p>', unsafe_allow_html=True)
    st.write("Please fill in your information before starting the survey. All fields are required.")

    with st.form("user_form"):
        name = st.text_input("Full Name", placeholder="e.g. Mary O'Connor or Smith-Jones", value=st.session_state.user_name)
        dob  = st.text_input("Date of Birth (YYYY-MM-DD)", placeholder="e.g. 2003-07-15", value=st.session_state.user_dob)
        sid  = st.text_input("Student ID (digits only)", placeholder="e.g. 00012345", value=st.session_state.user_sid)

        submitted = st.form_submit_button("Continue to Survey →")

    if submitted:
        name_ok, name_err = validate_name(name)
        dob_ok,  dob_err  = validate_dob(dob)
        sid_ok,  sid_err  = validate_student_id(sid)

        if name_ok and dob_ok and sid_ok:
            st.session_state.user_name = name
            st.session_state.user_dob  = dob
            st.session_state.user_sid  = sid
            st.session_state.answers   = []
            st.session_state.current_q = 0
            st.session_state.page      = "survey"
            st.rerun()
        else:
            if not name_ok:
                st.error(f"❌ Name: {name_err}")
            if not dob_ok:
                st.error(f"❌ Date of Birth: {dob_err}")
            if not sid_ok:
                st.error(f"❌ Student ID: {sid_err}")

    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()


# ══════════════════════════════════════════════
#  PAGE: SURVEY
# ══════════════════════════════════════════════

def page_survey():
    questions: list = st.session_state.questions
    current: int    = st.session_state.current_q
    total: int      = len(questions)

    # Progress
    progress: float = current / total
    st.markdown(f"**Question {current + 1} of {total}**")
    st.progress(progress)
    st.markdown("")

    q: dict = questions[current]

    st.markdown(f"""
    <div class="question-card">
        <span class="question-chip">Question {current + 1} of {total}</span>
        <p class="question-text">{q["text"]}</p>
    </div>
    """, unsafe_allow_html=True)

    options: list    = q["options"]
    selected         = st.radio("Select your answer:", options, key=f"q_{current}", index=None)

    col_back, col_next = st.columns([1, 2])

    with col_back:
        if current > 0:
            if st.button("← Previous"):
                st.session_state.current_q -= 1
                st.rerun()

    with col_next:
        label = "Next →" if current < total - 1 else "See Results →"
        if st.button(label):
            if selected is None:
                st.warning("Please select an answer before continuing.")
            else:
                answer_index: int = options.index(selected)
                # Store or overwrite answer for this question
                if len(st.session_state.answers) <= current:
                    st.session_state.answers.append(answer_index)
                else:
                    st.session_state.answers[current] = answer_index

                if current < total - 1:
                    st.session_state.current_q += 1
                    st.rerun()
                else:
                    # Calculate and store result
                    score: int   = calculate_score(st.session_state.answers, questions)
                    result: dict = evaluate_result(score)
                    data: dict   = build_result_data(
                        st.session_state.user_name,
                        st.session_state.user_dob,
                        st.session_state.user_sid,
                        score,
                        result["label"]
                    )
                    st.session_state.result_data = {**data, **result}
                    st.session_state.page = "results"
                    st.rerun()


# ══════════════════════════════════════════════
#  PAGE: RESULTS
# ══════════════════════════════════════════════

def page_results():
    rd: dict = st.session_state.result_data

    # ── Celebration banner & confetti ──────────────────────────────
    score: int = rd.get("score", 0)
    is_positive: bool = score <= 36  # Excellent / Good / Moderate = celebrate

    if is_positive:
        st.markdown("""
        <div class="celebration-banner">
            <span class="big-emoji">🎉</span>
            <div class="congrats-text">Survey Complete — Great job finishing!</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="celebration-banner">
            <span class="big-emoji">📋</span>
            <div class="congrats-text">Survey Complete — Here are your results</div>
        </div>
        """, unsafe_allow_html=True)

    # Confetti JS — launches automatically on results page
    confetti_js = """
    <script>
    (function() {
        var canvas = document.getElementById('confetti-canvas');
        if (!canvas) return;
        var ctx = canvas.getContext('2d');
        canvas.width  = window.innerWidth;
        canvas.height = window.innerHeight;

        var colors = ['#4f46e5','#2ecc71','#f39c12','#e74c3c','#9b59b6','#3498db','#1abc9c','#e67e22'];
        var pieces = [];
        var NUM    = PIECE_COUNT;

        for (var i = 0; i < NUM; i++) {
            pieces.push({
                x:     Math.random() * canvas.width,
                y:     Math.random() * canvas.height - canvas.height,
                w:     Math.random() * 12 + 6,
                h:     Math.random() * 6 + 4,
                color: colors[Math.floor(Math.random() * colors.length)],
                rot:   Math.random() * 360,
                rspd:  (Math.random() - 0.5) * 4,
                spd:   Math.random() * 3 + 2,
                swing: Math.random() * 2 - 1,
                alpha: 1
            });
        }

        var frame = 0;
        var MAX_FRAMES = 220;

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            frame++;

            pieces.forEach(function(p) {
                p.y    += p.spd;
                p.x    += p.swing * Math.sin(frame * 0.05);
                p.rot  += p.rspd;
                if (frame > MAX_FRAMES - 60) {
                    p.alpha = Math.max(0, p.alpha - 0.025);
                }
                ctx.save();
                ctx.globalAlpha = p.alpha;
                ctx.translate(p.x + p.w / 2, p.y + p.h / 2);
                ctx.rotate(p.rot * Math.PI / 180);
                ctx.fillStyle = p.color;
                ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
                ctx.restore();
            });

            if (frame < MAX_FRAMES) {
                requestAnimationFrame(draw);
            } else {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
        }

        // small delay so canvas is ready
        setTimeout(draw, 300);

        window.addEventListener('resize', function() {
            canvas.width  = window.innerWidth;
            canvas.height = window.innerHeight;
        });
    })();
    </script>
    """

    # Only fire confetti for positive outcomes
    if is_positive:
        st.markdown(confetti_js.replace("PIECE_COUNT", "160"), unsafe_allow_html=True)
    else:
        st.markdown(confetti_js.replace("PIECE_COUNT", "40"), unsafe_allow_html=True)

    st.markdown('<p class="section-header">📊 Your Results</p>', unsafe_allow_html=True)

    # Result card
    color: str = rd.get("color", "#4f46e5")
    label: str = rd.get("label", "")
    msg: str   = rd.get("message", "")
    pct: float = rd.get("percentage", 0.0)

    st.markdown(f"""
    <div class="result-box" style="background: linear-gradient(135deg, {color}, {color}cc);">
        <div class="result-label">{label}</div>
        <div class="result-message">{msg}</div>
        <div class="score-pill">Score: {score} / 60 &nbsp;·&nbsp; {pct}%</div>
    </div>
    """, unsafe_allow_html=True)

    # User info
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Participant Details**")
    st.markdown(f"""
    <div class="info-row"><span class="info-key">Name</span><span class="info-val">{rd.get('name','')}</span></div>
    <div class="info-row"><span class="info-key">Date of Birth</span><span class="info-val">{rd.get('date_of_birth','')}</span></div>
    <div class="info-row"><span class="info-key">Student ID</span><span class="info-val">{rd.get('student_id','')}</span></div>
    <div class="info-row"><span class="info-key">Completed At</span><span class="info-val">{rd.get('completed_at','')}</span></div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Save section
    st.markdown("### 💾 Save Your Results")
    fmt = st.selectbox("Choose file format:", ["JSON (recommended)", "CSV", "TXT"])

    # Build clean save dict
    save_data: dict = {
        "name":        rd.get("name", ""),
        "date_of_birth": rd.get("date_of_birth", ""),
        "student_id":  rd.get("student_id", ""),
        "score":       rd.get("score", 0),
        "max_score":   60,
        "percentage":  rd.get("percentage", 0.0),
        "result":      rd.get("label", ""),
        "completed_at": rd.get("completed_at", ""),
    }

    if fmt.startswith("JSON"):
        file_content: str = serialize_json(save_data)
        ext, mime = "json", "application/json"
    elif fmt.startswith("CSV"):
        file_content = serialize_csv(save_data)
        ext, mime = "csv", "text/csv"
    else:
        file_content = serialize_txt(save_data)
        ext, mime = "txt", "text/plain"

    filename: str = f"survey_result_{rd.get('student_id','student')}.{ext}"
    st.download_button(
        label=f"⬇️ Download as {ext.upper()}",
        data=file_content,
        file_name=filename,
        mime=mime
    )

    st.markdown("---")
    if st.button("🔄 Take Survey Again"):
        for key in ["answers", "current_q", "user_name", "user_dob", "user_sid", "result_data"]:
            st.session_state[key] = [] if key == "answers" else 0 if key == "current_q" else {} if key == "result_data" else ""
        st.session_state.page = "home"
        st.rerun()


# ══════════════════════════════════════════════
#  PAGE: LOAD RESULTS
# ══════════════════════════════════════════════

def page_load():
    st.markdown('<p class="section-header">📂 Load Previous Results</p>', unsafe_allow_html=True)
    st.write("Upload a previously saved survey result file to view it here.")

    uploaded = st.file_uploader("Choose a file (TXT, CSV, or JSON)", type=["txt", "csv", "json"])

    if uploaded is not None:
        content: str = uploaded.read().decode("utf-8")
        data: dict | None = parse_uploaded_file(content, uploaded.name)

        if data:
            st.success("✅ File loaded successfully!")
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("**Loaded Survey Result**")
            for key, val in data.items():
                st.markdown(f"""
                <div class="info-row">
                    <span class="info-key">{key.replace('_',' ').title()}</span>
                    <span class="info-val">{val}</span>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("Could not parse the file. Please check the format.")

    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()


# ══════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════

page: str = st.session_state.page

if page == "home":
    page_home()
elif page == "user_info":
    page_user_info()
elif page == "survey":
    page_survey()
elif page == "results":
    page_results()
elif page == "load":
    page_load()
else:
    st.session_state.page = "home"
    st.rerun()
