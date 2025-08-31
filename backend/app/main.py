from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from app.auth import router as auth_router
from app.funds import router as funds_router
from app.fundDetail import router as fund_detail_router
from app.questionnaire import router as questionnaire_router
from app.routers.users import router as users_router
from app.routers.mutualfunds import router as mf_router


# Database & Models
from app.database import engine, Base
from app import models

# ---------------------------
# FastAPI app initialization
# ---------------------------
app = FastAPI(title="Mutual Funds API (dev)")

# ---------------------------
# CORS middleware
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Include routers
# ---------------------------
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(funds_router, prefix="/api/funds", tags=["Funds"])
app.include_router(questionnaire_router, prefix="/api/questionnaire", tags=["Questionnaire"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(mf_router, prefix="/api/mutual-funds", tags=["Mutual Funds Database"])
app.include_router(fund_detail_router, prefix="/api/mutual-funds/risk", tags=["Mutual Funds Risk"])

# ---------------------------
# Root endpoint
# ---------------------------
@app.get("/")
async def root():
    return {"message": "Hello from FastAPI (dev)"}

# ---------------------------
# Startup: initialize DB
# ---------------------------
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created")
