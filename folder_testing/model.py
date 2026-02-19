# models.py

class Student:
    def __init__(self, student_id: str, name: str, age: int, marks: float):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.marks = marks

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "age": self.age,
            "marks": self.marks
        }

    @staticmethod
    def from_dict(data: dict):
        return Student(
            student_id=data["student_id"],
            name=data["name"],
            age=data["age"],
            marks=data["marks"]
        )
