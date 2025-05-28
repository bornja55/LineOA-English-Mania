from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "user"  # ชื่อตารางตรงกับฐานข้อมูล
    user_id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=True)
    line_user_id = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)

class Enrollment(Base):
    __tablename__ = "enrollment"  # ชื่อตารางตรงกับฐานข้อมูล
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.id"))
    course_id = Column(Integer, ForeignKey("course.id"))
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("student", back_populates="enrollment")
    course = relationship("course", back_populates="enrollment")

class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    line_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrollments = relationship("enrollment", back_populates="student")
    attendances = relationship("attendance", back_populates="student")

class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrollments = relationship("enrollment", back_populates="course")
    teacher_id = Column(Integer, ForeignKey("teacher.id"), nullable=True)
    teacher = relationship("teacher", back_populates="courses")
    attendances = relationship("attendance", back_populates="course")

class Teacher(Base):
    __tablename__ = "teacher"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ความสัมพันธ์กับตารางอื่น (เช่น Course ถ้ามี)
    courses = relationship("Course", back_populates="teacher")


class Classroom(Base):
    __tablename__ = "classroom"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    capacity = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ความสัมพันธ์กับตารางอื่น (เช่น Schedule ถ้ามี)
    schedules = relationship("schedule", back_populates="classroom")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)  # เช่น "present", "absent", "late"
    note = Column(String, nullable=True)

    student = relationship("student", back_populates="attendances")
    course = relationship("course", back_populates="attendances")