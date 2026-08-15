from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


# ======================================================
# USER MODEL
# ======================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        nullable=False
    )

    jobs = relationship(
        "Job",
        back_populates="employer",
        cascade="all, delete-orphan"
    )

    applications = relationship(
        "Application",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# ======================================================
# JOB MODEL
# ======================================================

class Job(Base):

    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(200),
        nullable=False
    )

    company = Column(
        String(200),
        nullable=False
    )

    location = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    requirements = Column(
        Text,
        nullable=True
    )

    salary = Column(
        String(100),
        nullable=True
    )

    job_type = Column(
        String(100),
        nullable=True
    )

    employer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    employer = relationship(
        "User",
        back_populates="jobs"
    )

    applications = relationship(
        "Application",
        back_populates="job",
        cascade="all, delete-orphan"
    )


# ======================================================
# APPLICATION MODEL
# ======================================================

class Application(Base):

    __tablename__ = "applications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    status = Column(
        String(50),
        default="pending",
        nullable=False
    )

    job = relationship(
        "Job",
        back_populates="applications"
    )

    user = relationship(
        "User",
        back_populates="applications"
    )