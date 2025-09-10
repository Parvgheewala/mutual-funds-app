from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, List, Optional

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
            {"text": "Long-term (retirement, kids' education)", "points": 5},
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
            {"text": "Doesn't matter, long-term only", "points": 5},
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

# Data models
class Answer(BaseModel):
    question_id: int
    answer_index: int

class QuestionnaireResponse(BaseModel):
    next_question: Optional[dict] = None
    score: Optional[int] = None
    category: Optional[str] = None
    recommended_funds: Optional[List[dict]] = None
    is_complete: bool = False

# In-memory session storage (consider using Redis for production)
user_sessions: Dict[str, Dict] = {}

def get_risk_category(score: int) -> str:
    """Map score to risk category"""
    for low, high, category in SCORE_RANGES:
        if low <= score <= high:
            return category
    return "Unclassified"

async def get_fund_recommendations(user_risk_score: int, user_category: str) -> List[dict]:
    """Get personalized fund recommendations based on user profile"""
    # TODO: Implement your ML recommendation logic here
    # This is a placeholder that returns mock recommendations
    
    mock_recommendations = [
        {
            "fund_id": "120503",
            "fund_name": "HDFC Balanced Advantage Fund",
            "risk_score": 45.2,
            "expected_return": "12-15%",
            "category": "Hybrid"
        },
        {
            "fund_id": "118989",
            "fund_name": "SBI Bluechip Fund",
            "risk_score": 52.1,
            "expected_return": "14-18%",
            "category": "Large Cap"
        }
    ]
    
    # Filter based on user risk profile
    if user_risk_score < 30:  # Conservative
        return [r for r in mock_recommendations if r["risk_score"] < 40]
    elif user_risk_score > 45:  # Aggressive
        return [r for r in mock_recommendations if r["risk_score"] > 45]
    else:  # Balanced
        return mock_recommendations

@router.get("/questions", response_model=dict)
async def get_questions():
    """Get all questionnaire questions"""
    return {
        "questions": QUESTIONS,
        "total_questions": len(QUESTIONS),
        "scoring_ranges": SCORE_RANGES
    }

@router.post("/submit/{user_id}", response_model=QuestionnaireResponse)
async def submit_answer(user_id: str, answer: Answer):
    """Submit answer for a specific question and get next question or final result"""
    
    # Validate question ID
    if not any(q["id"] == answer.question_id for q in QUESTIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid question ID"
        )

    # Get question details
    question = next(q for q in QUESTIONS if q["id"] == answer.question_id)
    
    # Validate answer index
    if answer.answer_index < 0 or answer.answer_index >= len(question["options"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid answer index"
        )

    # Initialize user session if new
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "score": 0,
            "answered": set(),
            "answers": {}  # Store individual answers for analysis
        }

    # Check for duplicate answer
    if answer.question_id in user_sessions[user_id]["answered"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question already answered"
        )

    # Update user session
    points = question["options"][answer.answer_index]["points"]
    user_sessions[user_id]["score"] += points
    user_sessions[user_id]["answered"].add(answer.question_id)
    user_sessions[user_id]["answers"][answer.question_id] = {
        "answer_index": answer.answer_index,
        "answer_text": question["options"][answer.answer_index]["text"],
        "points": points
    }

    # Check if questionnaire is complete
    remaining_questions = [q for q in QUESTIONS if q["id"] not in user_sessions[user_id]["answered"]]
    
    if remaining_questions:
        # Return next question
        return QuestionnaireResponse(
            next_question=remaining_questions[0],
            is_complete=False
        )
    
    # All questions completed - calculate final result
    total_score = user_sessions[user_id]["score"]
    category = get_risk_category(total_score)
    
    # Get personalized recommendations
    recommendations = await get_fund_recommendations(total_score, category)
    
    # Clean up session after completion
    del user_sessions[user_id]
    
    return QuestionnaireResponse(
        score=total_score,
        category=category,
        recommended_funds=recommendations,
        is_complete=True
    )

@router.get("/progress/{user_id}")
async def get_progress(user_id: str):
    """Get current progress for a user"""
    if user_id not in user_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User session not found"
        )
    
    session = user_sessions[user_id]
    progress_percentage = (len(session["answered"]) / len(QUESTIONS)) * 100
    
    return {
        "user_id": user_id,
        "questions_answered": len(session["answered"]),
        "total_questions": len(QUESTIONS),
        "progress_percentage": round(progress_percentage, 1),
        "current_score": session["score"]
    }

@router.delete("/reset/{user_id}")
async def reset_questionnaire(user_id: str):
    """Reset questionnaire progress for a user"""
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    return {"message": f"Questionnaire reset for user {user_id}"}
