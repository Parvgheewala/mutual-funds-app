from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

QUESTIONS = [
    {"id": 1, "question": "What is your primary investment goal?",
     "options": [
         {"text": "To become financially independent", "points": 3},
         {"text": "To secure retirement", "points": 2},
         {"text": "To preserve capital", "points": 1},
         {"text": "To beat the market", "points": 4}
     ]},
    {"id": 2, "question": "What is your investment time horizon?",
     "options": [
         {"text": "Less than 1 year", "points": 1},
         {"text": "1–3 years", "points": 2},
         {"text": "3–5 years", "points": 3},
         {"text": "More than 5 years", "points": 4}
     ]},
    {"id": 3, "question": "Are you investing for specific life goals?",
     "options": [
         {"text": "Yes, within 2 years", "points": 2},
         {"text": "Yes, in 3–5 years", "points": 3},
         {"text": "Yes, more than 5 years", "points": 4},
         {"text": "No, for general growth", "points": 3}
     ]},
    {"id": 4, "question": "How would you react to a 25% loss in your portfolio?",
     "options": [
         {"text": "Panic and sell", "points": 1},
         {"text": "Worry but wait", "points": 2},
         {"text": "Stay calm and review", "points": 3},
         {"text": "Buy more", "points": 4}
     ]},
    {"id": 5, "question": "How do you respond to market volatility?",
     "options": [
         {"text": "Avoid investing", "points": 1},
         {"text": "Sell during dips", "points": 2},
         {"text": "Stick to the plan", "points": 3},
         {"text": "Buy on dips", "points": 4}
     ]},
    {"id": 6, "question": "What’s your instinct during global crises?",
     "options": [
         {"text": "Sell to protect capital", "points": 1},
         {"text": "Monitor but hold", "points": 2},
         {"text": "See as buying opportunity", "points": 3},
         {"text": "Stay unfazed", "points": 4}
     ]},
    {"id": 7, "question": "How would you describe your investment knowledge?",
     "options": [
         {"text": "Minimal", "points": 1},
         {"text": "Basic", "points": 2},
         {"text": "Moderate", "points": 3},
         {"text": "Advanced", "points": 4}
     ]},
    {"id": 8, "question": "Have you built a diversified portfolio before?",
     "options": [
         {"text": "No", "points": 1},
         {"text": "Yes, with help", "points": 2},
         {"text": "Yes, independently", "points": 3},
         {"text": "Yes, and I monitor it", "points": 4}
     ]},
    {"id": 9, "question": "How often do you review your investments?",
     "options": [
         {"text": "Rarely", "points": 1},
         {"text": "Occasionally", "points": 2},
         {"text": "Monthly", "points": 3},
         {"text": "Weekly or daily", "points": 4}
     ]},
    {"id": 10, "question": "What percent of your income do you invest?",
     "options": [
         {"text": "0–10%", "points": 1},
         {"text": "11–25%", "points": 2},
         {"text": "26–50%", "points": 3},
         {"text": ">50%", "points": 4}
     ]},
    {"id": 11, "question": "Do you have an emergency fund (6+ months)?",
     "options": [
         {"text": "No, and it's a concern", "points": 1},
         {"text": "No, but I have liquid assets", "points": 2},
         {"text": "Yes, partially", "points": 3},
         {"text": "Yes, fully funded", "points": 4}
     ]},
    {"id": 12, "question": "How stable is your income?",
     "options": [
         {"text": "Unstable", "points": 1},
         {"text": "Slightly unstable", "points": 2},
         {"text": "Stable", "points": 3},
         {"text": "Very stable", "points": 4}
     ]},
    {"id": 13, "question": "How do you monitor your portfolio?",
     "options": [
         {"text": "Real-time alerts", "points": 4},
         {"text": "Weekly reports", "points": 3},
         {"text": "Monthly reports", "points": 2},
         {"text": "Rarely or on events", "points": 1}
     ]},
    {"id": 14, "question": "What’s your reaction if your portfolio outperforms the market?",
     "options": [
         {"text": "Take more risk", "points": 4},
         {"text": "Stick to plan", "points": 3},
         {"text": "Take profits", "points": 2},
         {"text": "Ignore, focus on long-term", "points": 1}
     ]},
    {"id": 15, "question": "What is your preferred investment style?",
     "options": [
         {"text": "Actively manage myself", "points": 4},
         {"text": "Mix of active and passive", "points": 3},
         {"text": "Passive with help", "points": 2},
         {"text": "Leave to advisor", "points": 1}
     ]},
    {"id": 16, "question": "Are you interested in ESG or ethical investing?",
     "options": [
         {"text": "Yes, strongly", "points": 3},
         {"text": "Somewhat", "points": 2},
         {"text": "Not really", "points": 1},
         {"text": "No preference", "points": 1}
     ]},
    {"id": 17, "question": "How do you handle investment losses?",
     "options": [
         {"text": "Exit immediately", "points": 1},
         {"text": "Wait and watch", "points": 2},
         {"text": "Stick to strategy", "points": 3},
         {"text": "Buy more", "points": 4}
     ]},
    {"id": 18, "question": "Do you prefer long-term compounding or short-term gains?",
     "options": [
         {"text": "Short-term trades", "points": 1},
         {"text": "Mix of both", "points": 2},
         {"text": "Prefer long-term", "points": 3},
         {"text": "Long-term only", "points": 4}
     ]},
    {"id": 19, "question": "How involved do you want to be in managing your investments?",
     "options": [
         {"text": "Full control", "points": 4},
         {"text": "High involvement", "points": 3},
         {"text": "Minimal involvement", "points": 2},
         {"text": "Leave it to professionals", "points": 1}
     ]},
    {"id": 20, "question": "Do you value simplicity over performance?",
     "options": [
         {"text": "Strongly yes", "points": 1},
         {"text": "Somewhat", "points": 2},
         {"text": "No", "points": 3},
         {"text": "Prefer complexity with better returns", "points": 4}
     ]}
]


SCORE_RANGES = [
    (15, 25, "Ultra-Conservative"),
    (26, 32, "Conservative"),
    (28, 38, "Income-Oriented"),
    (33, 44, "Balanced / Moderate"),
    (45, 54, "Growth-Oriented"),
    (55, 65, "Aggressive Growth"),
    (60, 75, "Speculative")
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
    result = next((cat for low, high, cat in SCORE_RANGES 
                  if low <= score <= high), "Unclassified")
    del user_data[user_id]
    return {"score": score, "result": result}