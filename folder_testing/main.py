# main.py

from models import Student
from database import Database
from analytics import Analytics


def run():
    db = Database()
    analytics = Analytics(db)

    while True:
        print("\n=== Smart Student Management System ===")
        print("1. Add Student")
        print("2. View All Students")
        print("3. Search by Name")
        print("4. Update Student")
        print("5. Remove Student")
        print("6. Analytics")
        print("7. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            sid = input("ID: ")
            name = input("Name: ")
            age = int(input("Age: "))
            marks = float(input("Marks: "))
            student = Student(sid, name, age, marks)
            db.add_student(student)
            print("Student added.")

        elif choice == "2":
            for s in db.get_all_students():
                print(s.to_dict())

        elif choice == "3":
            name = input("Enter name: ")
            results = db.search_by_name(name)
            for s in results:
                print(s.to_dict())

        elif choice == "4":
            sid = input("Student ID: ")
            new_marks = float(input("New Marks: "))
            db.update_student(sid, marks=new_marks)
            print("Updated.")

        elif choice == "5":
            sid = input("Student ID: ")
            db.remove_student(sid)
            print("Removed.")

        elif choice == "6":
            print("Average Marks:", analytics.average_marks())
            topper = analytics.topper()
            if topper:
                print("Topper:", topper.to_dict())

        elif choice == "7":
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    run()
