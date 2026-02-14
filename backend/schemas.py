from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date

# --- Shared Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# --- Client Schemas ---
class ClientBase(BaseModel):
    email: EmailStr
    number: Optional[str] = None

class ClientCreate(ClientBase):
    password: str

class Client(ClientBase):
    id_client: int
    
    class Config:
        orm_mode = True

# --- Employee Schemas ---
class EmployeeBase(BaseModel):
    email: EmailStr
    role: str
    number: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    password: str

class Employee(EmployeeBase):
    id_employee: int

    class Config:
        orm_mode = True

# --- Project Schemas ---
class ProjectBase(BaseModel):
    git_repo: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    duration: Optional[int] = None
    id_client: int

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id_project: int

    class Config:
        orm_mode = True

# --- Report Schemas ---
class ReportBase(BaseModel):
    creation_date: Optional[date] = None
    attachment: Optional[str] = None
    id_project: int

class ReportCreate(ReportBase):
    pass

class Report(ReportBase):
    id_report: int

    class Config:
        orm_mode = True

# --- Feedback Schemas ---
class FeedbackBase(BaseModel):
    feedback_date: Optional[date] = None
    text: str
    id_project: int
    id_client: int

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id_feedback: int

    class Config:
        orm_mode = True
