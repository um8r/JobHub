from pydantic import BaseModel, EmailStr


# =========================================
# USER
# =========================================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "job_seeker"


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


# =========================================
# LOGIN
# =========================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# =========================================
# JOB
# =========================================

class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    description: str
    requirements: str = ""
    salary: str = ""
    job_type: str = "Full Time"


class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str
    requirements: str
    salary: str
    job_type: str

    class Config:
        from_attributes = True


# =========================================
# APPLICATION
# =========================================

class ApplicationCreate(BaseModel):
    user_id: int


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    user_id: int
    status: str

    class Config:
        from_attributes = True