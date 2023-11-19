from dataclasses import dataclass, field

@dataclass
class Course:
    course_id: str
    name: str
    instructor: str
    credits: float

@dataclass
class Student:
    genesis_id: str
    name: str
    grade_level: str = None
    email: str = None
    homeroom: str = None

