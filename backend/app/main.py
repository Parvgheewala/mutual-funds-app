from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from app.auth import router as auth_router
from app.funds import router as funds_router
from app.questionnaire import router as questionnaire_router
from app.userdata import router as userdata_router
from .database import engine, Base
from .routers import users, mutualfunds
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
    allow_origins=["*"],          # In production, restrict to trusted domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Routers
# ---------------------------
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(funds_router, prefix="/api/funds", tags=["Funds"])
app.include_router(questionnaire_router, prefix="/api/questionnaire", tags=["Questionnaire"])
app.include_router(userdata_router, prefix="/api/userdata", tags=["User Data"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(mutualfunds.router, prefix="/mutual-funds", tags=["Mutual Funds"])

# ---------------------------
# Root endpoint
# ---------------------------
@app.get("/")
async def root():
    return {"message": "Hello from FastAPI (dev)"}

# ---------------------------
# Startup event
# ---------------------------
@app.on_event("startup")
async def on_startup():
    await models.init_models()
    print("✅ Database tables created")

