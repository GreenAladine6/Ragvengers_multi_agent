from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Text
from sqlalchemy.orm import relationship
from database import Base

class Client(Base):
    __tablename__ = "client"

    id_client = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    number = Column(String(20))

    projects = relationship("Project", back_populates="client")
    feedbacks = relationship("Feedback", back_populates="client")

class Employee(Base):
    __tablename__ = "employee"

    id_employee = Column(Integer, primary_key=True, index=True)
    role = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    number = Column(String(20))

    project_associations = relationship("ProjectEmployee", back_populates="employee")

class Project(Base):
    __tablename__ = "project"

    id_project = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    git_repo = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(50))
    duration = Column(Integer)
    progress_frontend = Column(Integer, default=0)
    progress_backend = Column(Integer, default=0)
    progress_database = Column(Integer, default=0)
    progress_chatbot = Column(Integer, default=0)
    id_client = Column(Integer, ForeignKey("client.id_client"), nullable=False)

    client = relationship("Client", back_populates="projects")
    report = relationship("Report", back_populates="project", uselist=False)
    feedbacks = relationship("Feedback", back_populates="project")
    employee_associations = relationship("ProjectEmployee", back_populates="project")

class ProjectEmployee(Base):
    __tablename__ = "project_employee"

    id_project = Column(Integer, ForeignKey("project.id_project"), primary_key=True)
    id_employee = Column(Integer, ForeignKey("employee.id_employee"), primary_key=True)

    project = relationship("Project", back_populates="employee_associations")
    employee = relationship("Employee", back_populates="project_associations")

class Report(Base):
    __tablename__ = "report"

    id_report = Column(Integer, primary_key=True, index=True)
    creation_date = Column(Date)
    attachment = Column(Text)
    id_project = Column(Integer, ForeignKey("project.id_project"), nullable=False)

    project = relationship("Project", back_populates="report")

class Feedback(Base):
    __tablename__ = "feedback"

    id_feedback = Column(Integer, primary_key=True, index=True)
    feedback_date = Column(Date)
    text = Column(Text, nullable=False)
    rating = Column(Integer)
    id_project = Column(Integer, ForeignKey("project.id_project"), nullable=False)
    id_client = Column(Integer, ForeignKey("client.id_client"), nullable=False)

    project = relationship("Project", back_populates="feedbacks")
    client = relationship("Client", back_populates="feedbacks")
