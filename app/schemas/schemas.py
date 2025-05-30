# schemas/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Role Schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int

    class Config:
        orm_mode = True

# User Schemas
class UserBase(BaseModel):
    username: Optional[str]
    name: Optional[str]
    email: Optional[EmailStr]

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: int
    role: Optional[RoleResponse] = None  # เพิ่ม role

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

class TokenData(BaseModel):
    user_id: int
    username: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str

class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str

class SuccessResponse(BaseModel):
    success: bool
    message: str

# Invoice Schemas
class InvoiceBase(BaseModel):
    student_id: int
    enrollment_id: int
    invoice_date: datetime
    due_date: datetime
    total_amount: float
    description: Optional[str] = None
    status: Optional[str] = "pending"

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceResponse(InvoiceBase):
    invoice_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Income Schemas
class IncomeBase(BaseModel):
    payment_id: int
    income_date: datetime
    income_type: Optional[str] = None
    amount: float
    description: Optional[str] = None

class IncomeCreate(IncomeBase):
    pass

class IncomeResponse(IncomeBase):
    income_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Expense Schemas
class ExpenseBase(BaseModel):
    expense_date: datetime
    expense_type: Optional[str] = None
    amount: float
    description: Optional[str] = None
    vendor: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    expense_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class PaymentBase(BaseModel):
    enrollment_id: int
    invoice_id: Optional[int] = None
    amount: float
    payment_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    slip_url: Optional[str] = None
    status: Optional[str] = "pending"

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int

    class Config:
        orm_mode = True

# เพื่อแก้ไข circular reference
CourseResponse.update_forward_refs()
TeacherResponse.update_forward_refs()
AttendanceResponse.update_forward_refs()
StudentResponse.update_forward_refs()