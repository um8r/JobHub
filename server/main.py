from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import User, Job, Application

from schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    JobCreate,
    JobResponse,
    ApplicationCreate,
    ApplicationResponse
)

from auth import (
    create_access_token,
    get_current_user,
    require_job_seeker,
    require_employer
)


# ======================================================
# DATABASE
# ======================================================

Base.metadata.create_all(bind=engine)


# ======================================================
# APP
# ======================================================

app = FastAPI(
    title="JobHub API",
    description="JobHub Full Stack Job Marketplace API",
    version="3.0.0"
)


# ======================================================
# CORS
# ======================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================================================
# DATABASE SESSION
# ======================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ======================================================
# ROOT
# ======================================================

@app.get("/")
def root():
    return {
        "message": "JobHub API is running",
        "status": "success",
        "version": "3.0.0"
    }


# ======================================================
# HEALTH
# ======================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "JobHub backend is working"
    }


# ======================================================
# REGISTER
# ======================================================

@app.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    role = str(user.role).lower().strip()

    if role not in [
        "job_seeker",
        "jobseeker",
        "employer"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    if role == "jobseeker":
        role = "job_seeker"

    new_user = User(
        name=user.name.strip(),
        email=user.email.strip().lower(),
        password=user.password,
        role=role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ======================================================
# LOGIN
# ======================================================

@app.post("/login")
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):

    email = credentials.email.strip().lower()

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if user.password != credentials.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }


# ======================================================
# CURRENT USER
# ======================================================

@app.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }


# ======================================================
# GET ALL JOBS
# ======================================================

@app.get(
    "/jobs",
    response_model=list[JobResponse]
)
def get_jobs(
    db: Session = Depends(get_db)
):

    return db.query(Job).order_by(
        Job.id.desc()
    ).all()


# ======================================================
# GET SINGLE JOB
# ======================================================

@app.get(
    "/jobs/{job_id}",
    response_model=JobResponse
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job


# ======================================================
# CREATE JOB
# EMPLOYER ONLY
# ======================================================

@app.post(
    "/jobs",
    response_model=JobResponse
)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer)
):

    new_job = Job(
        title=job.title.strip(),
        company=job.company.strip(),
        location=job.location.strip(),
        description=job.description.strip(),
        requirements=job.requirements,
        salary=job.salary,
        job_type=job.job_type,

        # IMPORTANT
        employer_id=current_user.id
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


# ======================================================
# DELETE JOB
# EMPLOYER ONLY
# ======================================================

@app.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer)
):

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own jobs"
        )

    db.query(Application).filter(
        Application.job_id == job_id
    ).delete(
        synchronize_session=False
    )

    db.delete(job)
    db.commit()

    return {
        "message": "Job and related applications deleted successfully"
    }


# ======================================================
# APPLY FOR JOB
# JOB SEEKER ONLY
# ======================================================

@app.post(
    "/jobs/{job_id}/apply",
    response_model=ApplicationResponse
)
def apply_for_job(
    job_id: int,
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_job_seeker)
):

    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only apply using your own account"
        )

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    existing = db.query(Application).filter(
        Application.job_id == job_id,
        Application.user_id == current_user.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="You already applied for this job"
        )

    new_application = Application(
        job_id=job_id,
        user_id=current_user.id,
        status="pending"
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return new_application


# ======================================================
# USER APPLICATIONS
# ======================================================

@app.get(
    "/users/{user_id}/applications",
    response_model=list[ApplicationResponse]
)
def get_user_applications(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own applications"
        )

    return db.query(Application).filter(
        Application.user_id == current_user.id
    ).order_by(
        Application.id.desc()
    ).all()


# ======================================================
# EMPLOYER APPLICATIONS
# ONLY APPLICATIONS FOR EMPLOYER'S JOBS
# ======================================================

@app.get(
    "/applications",
    response_model=list[ApplicationResponse]
)
def get_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer)
):

    applications = (
        db.query(Application)
        .join(Job, Application.job_id == Job.id)
        .filter(Job.employer_id == current_user.id)
        .order_by(Application.id.desc())
        .all()
    )

    return applications


# ======================================================
# UPDATE APPLICATION STATUS
# EMPLOYER ONLY
# ======================================================

@app.put(
    "/applications/{application_id}/status"
)
def update_application_status(
    application_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employer)
):

    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    job = db.query(Job).filter(
        Job.id == application.job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Related job not found"
        )

    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only manage applications for your own jobs"
        )

    status = status.lower().strip()

    allowed_statuses = [
        "pending",
        "reviewing",
        "accepted",
        "rejected"
    ]

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid application status"
        )

    application.status = status

    db.commit()
    db.refresh(application)

    return {
        "message": "Application status updated successfully",
        "application": application
    }