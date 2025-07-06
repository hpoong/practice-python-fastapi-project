from fastapi import FastAPI
from core.security import GlobalAuthMiddleware
from routers import user_router, admin_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(GlobalAuthMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(user_router.router)
app.include_router(admin_router.router)