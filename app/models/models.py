from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, Text, Date, Numeric
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("role.role_id"), nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=True)
    line_user_id = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)

    role = relationship("Role", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

class Role(Base):
    __tablename__ = "role"
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    users = relationship("User", back_populates="role")

class Student(Base):
    __tablename__ = "student"

    student_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    line_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    enrollments = relationship("Enrollment", back_populates="student")
    attendances = relationship("Attendance", back_populates="student")

class Course(Base):
    __tablename__ = "course"

    course_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    enrollments = relationship("Enrollment", back_populates="course")
    teacher_id = Column(Integer, ForeignKey("teacher.teacher_id"), nullable=True)
    teacher = relationship("Teacher", back_populates="courses")
    attendances = relationship("Attendance", back_populates="course")
    schedules = relationship("Schedule", back_populates="course")

class Enrollment(Base):
    __tablename__ = "enrollment"
    enrollment_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.student_id"))
    course_id = Column(Integer, ForeignKey("course.course_id"))
    enroll_date = Column(Date)
    expire_date = Column(Date)
    status = Column(String(20))

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class Teacher(Base):
    __tablename__ = "teacher"

    teacher_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    courses = relationship("Course", back_populates="teacher")

class Classroom(Base):
    __tablename__ = "classroom"

    classroom_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    capacity = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    schedules = relationship("Schedule", back_populates="classroom")

class Attendance(Base):
    __tablename__ = "attendance"

    attendance_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.student_id"), nullable=False)
    course_id = Column(Integer, ForeignKey("course.course_id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)  # เช่น "present", "absent", "late"
    note = Column(String, nullable=True)

    student = relationship("Student", back_populates="attendances")
    course = relationship("Course", back_populates="attendances")

class Schedule(Base):
    __tablename__ = "schedule"

    schedule_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.course_id"), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classroom.classroom_id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    course = relationship("Course", back_populates="schedules")
    classroom = relationship("Classroom", back_populates="schedules")

class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    user = relationship("User", back_populates="refresh_tokens")

class Invoice(Base):
    __tablename__ = "invoice"

    invoice_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.student_id"), nullable=False)
    enrollment_id = Column(Integer, ForeignKey("enrollment.enrollment_id"), nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    total_amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student")
    enrollment = relationship("Enrollment")
    payments = relationship("Payment", back_populates="invoice")

class Payment(Base):
    __tablename__ = "payment"

    payment_id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollment.enrollment_id"))
    invoice_id = Column(Integer, ForeignKey("invoice.invoice_id"), nullable=True)
    amount = Column(Float)
    payment_date = Column(DateTime)
    payment_method = Column(String)
    slip_url = Column(String)
    status = Column(String)
    payment_status = Column(String, default="pending")

    invoice = relationship("Invoice", back_populates="payments")
    enrollment = relationship("Enrollment")

class Income(Base):
    __tablename__ = "income"

    income_id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payment.payment_id"), nullable=False)
    income_date = Column(DateTime, nullable=False)
    income_type = Column(String(100), nullable=True)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    payment = relationship("Payment")

class Expense(Base):
    __tablename__ = "expense"

    expense_id = Column(Integer, primary_key=True, index=True)
    expense_date = Column(DateTime, nullable=False)
    expense_type = Column(String(100), nullable=True)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    vendor = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Exam(Base):
    __tablename__ = "exams"

    exam_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan")
    student_exams = relationship("StudentExam", back_populates="exam", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    question_id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.exam_id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # e.g. 'multiple_choice', 'fill_in_blank', 'essay'
    media_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    exam = relationship("Exam", back_populates="questions")
    choices = relationship("Choice", back_populates="question", cascade="all, delete-orphan")


class Choice(Base):
    __tablename__ = "choices"

    choice_id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.question_id", ondelete="CASCADE"), nullable=False)
    choice_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    question = relationship("Question", back_populates="choices")


class StudentExam(Base):
    __tablename__ = "student_exams"

    student_exam_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.student_id", ondelete="CASCADE"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.exam_id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    status = Column(String(50), default="in_progress")  # in_progress, completed
    score = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    exam = relationship("Exam", back_populates="student_exams")
    student = relationship("Student")  # Assuming Student model exists
    answers = relationship("StudentAnswer", back_populates="student_exam", cascade="all, delete-orphan")


class StudentAnswer(Base):
    __tablename__ = "student_answers"

    student_answer_id = Column(Integer, primary_key=True, index=True)
    student_exam_id = Column(Integer, ForeignKey("student_exams.student_exam_id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.question_id", ondelete="CASCADE"), nullable=False)
    choice_id = Column(Integer, ForeignKey("choices.choice_id"), nullable=True)
    answer_text = Column(Text, nullable=True)
    is_correct = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student_exam = relationship("StudentExam", back_populates="answers")
    question = relationship("Question")
    choice = relationship("Choice")