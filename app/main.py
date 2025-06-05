from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from .database import engine
from .models import models
from app.routers import students, courses, enrollments, auth, line_auth, line_webhook, invoice, finance, exams

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="English Mania API",
    description="API for English Mania School Management System",
    version="1.0.0"
)

origins = [
    "https://bornja55.github.io",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(auth.router)
app.include_router(line_auth.router)
app.include_router(line_webhook.router)
app.include_router(invoice.router)
app.include_router(finance.router)
app.include_router(exams.router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")
bearer_scheme = HTTPBearer()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/admin/login",
                    "scopes": {}
                }
            }
        },
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [
        {"OAuth2PasswordBearer": []},
        {"HTTPBearer": []}
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/")
def read_root():
    return {"message": "Welcome to English Mania API"}