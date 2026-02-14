from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, projects, chatbot, users
import database, models

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Ragvengers Backend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Ragvengers Backend"}

app.include_router(auth.router)
app.include_router(users.router, prefix="/users")
app.include_router(projects.router)
app.include_router(chatbot.router)
