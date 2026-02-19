# analytics.py

from database import Database


class Analytics:
    def __init__(self, db: Database):
        self.db = db

    def average_marks(self):
        students = self.db.get_all_students()
        if not students:
            return 0
        return sum(s.marks for s in students) / len(students)

    def topper(self):
        students = self.db.get_all_students()
        if not students:
            return None
        return max(students, key=lambda s: s.marks)

    def failing_students(self, threshold=40):
        return [s for s in self.db.get_all_students() if s.marks < threshold]
