from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

QUESTIONS = [
    {
        "id": 1,
        "question": "What is your age group?",
        "options": [
            {"text": "Below 25 years", "points": 5},
            {"text": "25–35 years", "points": 4},
            {"text": "36–45 years", "points": 3},
            {"text": "46–55 years", "points": 2},
            {"text": "56+ years", "points": 1},
        ],
    },
    {
        "id": 2,
        "question": "What is your type of occupation/income?",
        "options": [
            {"text": "Salaried (fixed income)", "points": 2},
            {"text": "Professional / Consultant (variable)", "points": 3},
            {"text": "Self-employed", "points": 4},
            {"text": "Business Owner (fluctuating income)", "points": 5},
        ],
    },
    {
        "id": 3,
        "question": "What is your annual income (INR)?",
        "options": [
            {"text": "< 5 Lakhs", "points": 1},
            {"text": "5–10 Lakhs", "points": 2},
            {"text": "10–25 Lakhs", "points": 3},
            {"text": "25–50 Lakhs", "points": 4},
            {"text": "50+ Lakhs", "points": 5},
        ],
    },
    {
        "id": 4,
        "question": "How many financial dependents do you support?",
        "options": [
            {"text": "5 or more", "points": 1},
            {"text": "3–4 dependents", "points": 2},
            {"text": "1–2 dependents", "points": 3},
            {"text": "None", "points": 5},
        ],
    },
    {
        "id": 5,
        "question": "What is your primary investment goal?",
        "options": [
            {"text": "Short-term (<3 years, vacation, car)", "points": 1},
            {"text": "Medium-term (3–5 years, house, education)", "points": 2},
            {"text": "Long-term (retirement, kids’ education)", "points": 5},
            {"text": "Regular Income requirement", "points": 2},
        ],
    },
    {
        "id": 6,
        "question": "Expected Liquidity Preference?",
        "options": [
            {"text": "Very high (instant access)", "points": 1},
            {"text": "Moderate (1–3 years)", "points": 3},
            {"text": "Low (okay with 5–10 years)", "points": 5},
        ],
    },
    {
        "id": 7,
        "question": "What annual return range do you expect?",
        "options": [
            {"text": "4–6% (very safe, FD-like)", "points": 1},
            {"text": "7–10% (safe MF/debt)", "points": 2},
            {"text": "11–15% (balanced funds, SIPs)", "points": 3},
            {"text": "16–20% (growth oriented equity)", "points": 4},
            {"text": "20%+ (aggressive / high growth)", "points": 5},
        ],
    },
    {
        "id": 8,
        "question": "Preferred profit pattern?",
        "options": [
            {"text": "Stable small gains", "points": 1},
            {"text": "Moderate consistency", "points": 2},
            {"text": "Balanced growth, some volatility", "points": 3},
            {"text": "High growth, high fluctuation", "points": 4},
            {"text": "Doesn’t matter, long-term only", "points": 5},
        ],
    },
    {
        "id": 9,
        "question": "How do you perceive investment risk?",
        "options": [
            {"text": "Not comfortable at all", "points": 1},
            {"text": "Accept small fluctuations", "points": 2},
            {"text": "Okay with moderate ups/downs", "points": 3},
            {"text": "High risk tolerance", "points": 4},
            {"text": "Very high tolerance, big losses are acceptable", "points": 5},
        ],
    },
    {
        "id": 10,
        "question": "Which lifestyle suits you most?",
        "options": [
            {"text": "Highly disciplined saver", "points": 1},
            {"text": "Conservative planner", "points": 2},
            {"text": "Balanced & calculative", "points": 3},
            {"text": "Ambitious growth-oriented", "points": 4},
            {"text": "Flamboyant / big dreamer", "points": 5},
        ],
    },
    {
        "id": 11,
        "question": "How would you rate your financial knowledge?",
        "options": [
            {"text": "Very limited (only FD/Gold/Real estate)", "points": 1},
            {"text": "Basic (knows MFs/Insurance)", "points": 2},
            {"text": "Moderate (aware of SIPs, asset mix)", "points": 3},
            {"text": "Advanced (NAVs, taxation, categories)", "points": 4},
            {"text": "Expert / Active market-following", "points": 5},
        ],
    },
    {
        "id": 12,
        "question": "How important is tax saving in your investments?",
        "options": [
            {"text": "Very high (tax saving is priority)", "points": 1},
            {"text": "Medium (balance tax vs growth)", "points": 3},
            {"text": "Low (focus only on growth)", "points": 5},
        ],
    },
]

# Scoring ranges (adjusted for 12 questions, max 60 points)
SCORE_RANGES = [
    (12, 20, "Ultra-Conservative"),
    (21, 30, "Conservative but Calculative"),
    (31, 40, "Balanced Growth"),
    (41, 50, "Aggressive Growth"),
    (51, 60, "Flamboyant / Risk Taker"),
]


class Answer(BaseModel):
    question_id: int
    answer_index: int


user_data = {}


@router.get("/questions")
async def get_questions():
    return {"questions": QUESTIONS}


@router.post("/submit/{user_id}")
async def submit_answer(user_id: str, answer: Answer):
    if not any(q["id"] == answer.question_id for q in QUESTIONS):
        raise HTTPException(400, "Invalid question ID")

    q = next(q for q in QUESTIONS if q["id"] == answer.question_id)
    if answer.answer_index < 0 or answer.answer_index >= len(q["options"]):
        raise HTTPException(400, "Invalid answer index")

    if user_id not in user_data:
        user_data[user_id] = {"score": 0, "answered": set()}

    if answer.question_id in user_data[user_id]["answered"]:
        raise HTTPException(400, "Question already answered")

    points = q["options"][answer.answer_index]["points"]
    user_data[user_id]["score"] += points
    user_data[user_id]["answered"].add(answer.question_id)

    for nq in QUESTIONS:
        if nq["id"] not in user_data[user_id]["answered"]:
            return {"next_question": nq}

    score = user_data[user_id]["score"]
    result = next(
        (cat for low, high, cat in SCORE_RANGES if low <= score <= high),
        "Unclassified",
    )
    del user_data[user_id]
    return {"score": score, "result": result}
