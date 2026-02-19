# database.py

import json
import os
from models import Student


class Database:
    def __init__(self, file_path="students.json"):
        self.file_path = file_path
        self.students = self._load()

    def _load(self):
        if not os.path.exists(self.file_path):
            return []

        with open(self.file_path, "r") as f:
            data = json.load(f)
            return [Student.from_dict(item) for item in data]

    def _save(self):
        with open(self.file_path, "w") as f:
            json.dump([s.to_dict() for s in self.students], f, indent=4)

    def add_student(self, student: Student):
        if self.exists(student.student_id):
            raise ValueError("Student ID already exists.")
        self.students.append(student)
        self._save()

    def remove_student(self, student_id: str):
        self.students = [s for s in self.students if s.student_id != student_id]
        self._save()

    def get_student(self, student_id: str):
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None

    def get_all_students(self):
        return self.students

    def update_student(self, student_id: str, **kwargs):
        student = self.get_student(student_id)
        if not student:
            raise ValueError("Student not found.")

        for key, value in kwargs.items():
            if hasattr(student, key):
                setattr(student, key, value)

        self._save()

    def search_by_name(self, name: str):
        return [s for s in self.students if name.lower() in s.name.lower()]

    def clear_database(self):
        self.students = []
        self._save()

    def count_students(self):
        return len(self.students)

    def exists(self, student_id: str):
        return any(s.student_id == student_id for s in self.students)
