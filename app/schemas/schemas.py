from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: Optional[str]
    name: Optional[str]
    email: Optional[EmailStr]

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: int

    class Config:
        orm_mode = True

# Enrollment Schemas
class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentResponse(EnrollmentBase):
    id: int
    enrolled_at: datetime

    class Config:
        orm_mode = True

# Student Schemas
class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    line_id: Optional[str] = None

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    enrollments: List[EnrollmentResponse] = []
    # attendances: List[AttendanceResponse] = []  # ถ้าต้องการแสดง attendances ด้วย

    class Config:
        orm_mode = True

# Course Schemas
class CourseBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class CourseCreate(CourseBase):
    teacher_id: Optional[int] = None

class CourseResponse(CourseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    teacher: Optional["TeacherResponse"] = None
    enrollments: List[EnrollmentResponse] = []
    # attendances: List[AttendanceResponse] = []

    class Config:
        orm_mode = True

# Teacher Schemas
class TeacherBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class TeacherCreate(TeacherBase):
    pass

class TeacherResponse(TeacherBase):
    id: int
    created_at: datetime
    updated_at: datetime
    courses: List[CourseResponse] = []

    class Config:
        orm_mode = True

# Classroom Schemas
class ClassroomBase(BaseModel):
    name: str
    location: Optional[str] = None
    capacity: Optional[int] = None

class ClassroomCreate(ClassroomBase):
    pass

class ClassroomResponse(ClassroomBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Attendance Schemas
class AttendanceBase(BaseModel):
    student_id: int
    course_id: int
    date: Optional[datetime] = None
    status: str
    note: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(AttendanceBase):
    id: int
    date: datetime
    student: Optional[StudentResponse] = None
    course: Optional[CourseResponse] = None

    class Config:
        orm_mode = True

class LineLoginRequest(BaseModel):
    id_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int
    username: Optional[str] = None

class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str

class SuccessResponse(BaseModel):
    success: bool
    message: str


# เพื่อแก้ไข circular reference
CourseResponse.update_forward_refs()
TeacherResponse.update_forward_refs()
AttendanceResponse.update_forward_refs()
StudentResponse.update_forward_refs()