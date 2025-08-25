from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import router as auth_router
from app.funds import router as funds_router
from app.questionnaire import router as questionnaire_router
from app.userdata import router as userdata_router



# Create app ONCE at the top
app = FastAPI(title="Mutual Funds API (dev)")

# Add CORS middleware BEFORE routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Then include all routers
app.include_router(auth_router, prefix="/api/auth")
app.include_router(funds_router, prefix="/api/funds")
app.include_router(questionnaire_router, prefix="/api/questionnaire")
app.include_router(userdata_router, prefix="/api/userdata")

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI (dev)"}
