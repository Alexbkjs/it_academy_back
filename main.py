from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.user_routes import router as user_router
from app.api.quest_routes import router as quest_router
from app.api.leaderboard import router as leaderboard

from app.utils.auth_middleware import AuthMiddleware

import logging


# Create an instance of the FastAPI application
app = FastAPI()

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Add the AuthMiddleware to the app
app.add_middleware(AuthMiddleware)

# Add CORS (Cross-Origin Resource Sharing) middleware to allow requests from the specified origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Specify the frontend origin allowed to make requests to the backend
    allow_credentials=True,  # Allow cookies and credentials to be included in requests
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers in requests
)

api_prefix = "/api/v1"

# Include the user routes from the user_routes module under the /api prefix with the tag "users"
app.include_router(user_router, prefix=api_prefix, tags=["users"])

# Include the quest routes from the quest_routes module under the /api prefix with the tag "quests"
app.include_router(
    quest_router, prefix=api_prefix, tags=["quests"]
)  # Include quest routes

# Include the user routes from the leaderboard module under the /api prefix with the tag "leaderboard"
app.include_router(leaderboard, prefix=api_prefix, tags=["leaderboard"])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
