from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import create_tables_if_needed

# Routers
from app.auth import router as auth_router
from app.funds import router as funds_router
from app.fundDetail import router as fund_detail_router
from app.questionnaire import router as questionnaire_router
from app.routers.users import router as users_router
from app.routers.mutualfunds import router as mf_router
from app.routers.nav_store import router as navs_store_router

# Ormar database connect/disconnect helpers
from app.database import connect_to_db, disconnect_from_db

# ---------------------------
# Lifespan management
# ---------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_db()
    await create_tables_if_needed()  # Add 'await' here
    print("✅ Database connected and tables created")
    
    yield
    
    # Shutdown
    await disconnect_from_db()
    print("✅ Database disconnected")

# ---------------------------
# FastAPI app initialization (SINGLE INSTANCE)
# ---------------------------
app = FastAPI(
    title="Mutual Funds API (dev)",
    lifespan=lifespan
)

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
app.include_router(navs_store_router, prefix="/api/mutual-funds/navs", tags=["NAVs store"])

# ---------------------------
# Root endpoint
# ---------------------------
@app.get("/")
async def root():
    return {"message": "Hello from FastAPI (dev)"}

# Remove the old @app.on_event handlers - they're now in the lifespan function
