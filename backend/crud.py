from sqlalchemy.orm import Session
import models, schemas
from auth import get_password_hash

# --- Client CRUD ---
def get_client(db: Session, client_id: int):
    return db.query(models.Client).filter(models.Client.id_client == client_id).first()

def get_client_by_email(db: Session, email: str):
    return db.query(models.Client).filter(models.Client.email == email).first()

def create_client(db: Session, client: schemas.ClientCreate):
    hashed_password = get_password_hash(client.password)
    db_client = models.Client(email=client.email, password=hashed_password, number=client.number)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

# --- Employee CRUD ---
def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.id_employee == employee_id).first()

def get_employee_by_email(db: Session, email: str):
    return db.query(models.Employee).filter(models.Employee.email == email).first()

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    hashed_password = get_password_hash(employee.password)
    db_employee = models.Employee(email=employee.email, password=hashed_password, role=employee.role, number=employee.number)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

# --- Project CRUD ---
def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# --- Feedback CRUD ---
def create_feedback(db: Session, feedback: schemas.FeedbackCreate):
    db_feedback = models.Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def get_feedbacks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Feedback).offset(skip).limit(limit).all()
