import json
import os
import sqlite3
from contextlib import closing
from datetime import date

DATABASE_NAME = "tasks.db"
LEGACY_FILE_NAME = "tasks.json"


def initialize_database(connection):
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            deadline TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT ''
        )
        """
    )
    connection.commit()


def migrate_json_tasks(connection):
    if not os.path.exists(LEGACY_FILE_NAME):
        return

    try:
        with open(LEGACY_FILE_NAME, "r") as file:
            tasks = json.load(file)
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the tasks file.")
        return

    if not isinstance(tasks, list):
        print("Error: The tasks JSON file must contain a list.")
        return

    connection.executemany(
        """
        INSERT INTO tasks (title, completed, deadline, created_at, note)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                task.get("Title", ""),
                int(bool(task.get("completed", False))),
                task.get("deadline", ""),
                task.get("created_at", date.today().isoformat()),
                task.get("note", ""),
            )
            for task in tasks
            if isinstance(task, dict) and task.get("Title")
        ],
    )
    connection.commit()
    os.replace(LEGACY_FILE_NAME, f"{LEGACY_FILE_NAME}.migrated")


def load_tasks():
    with closing(sqlite3.connect(DATABASE_NAME)) as connection:
        initialize_database(connection)
        if connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0:
            migrate_json_tasks(connection)
        rows = connection.execute(
            """
            SELECT title, completed, deadline, created_at, note
            FROM tasks
            ORDER BY id
            """
        ).fetchall()
    return [
        {
            "Title": title,
            "completed": bool(completed),
            "deadline": deadline,
            "created_at": created_at,
            "note": note,
        }
        for title, completed, deadline, created_at, note in rows
    ]
    

def save_tasks(tasks):
    with closing(sqlite3.connect(DATABASE_NAME)) as connection:
        initialize_database(connection)
        connection.execute("DELETE FROM tasks")
        connection.executemany(
            """
            INSERT INTO tasks (title, completed, deadline, created_at, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    task["Title"],
                    int(bool(task["completed"])),
                    task.get("deadline", ""),
                    task.get("created_at", date.today().isoformat()),
                    task.get("note", ""),
                )
                for task in tasks
            ],
        )
        connection.commit()


def deadline_sort_key(task):
    deadline = task.get("deadline", "").strip()
    if not deadline:
        return (2, "")
    try:
        return (0, date.fromisoformat(deadline))
    except ValueError:
        return (1, deadline.casefold())

def view_tasks(tasks):
    if not tasks:
        print("No tasks found.")
    else:
        tasks_to_view = tasks
        if any(task.get("deadline") for task in tasks):
            print("\nView tasks by:")
            print("1. Deadline (soonest first)")
            print("2. Creation date (latest to oldest)")
            while True:
                choice = input("Enter your choice (1-2): ").strip()
                if choice in ("1", "2"):
                    break
                print("Invalid choice. Please enter 1 or 2.")

            if choice == "1":
                tasks_to_view = sorted(tasks, key=deadline_sort_key)
            else:
                tasks_to_view = sorted(
                    tasks,
                    key=lambda task: task.get("created_at", ""),
                    reverse=True, #puts the recent task first
                )

        print("\n------ TASKS ------")
        for index, task in enumerate(tasks_to_view, start=1):
            status = "Done" if task["completed"] else "Pending"
            deadline = f" (Deadline: {task.get('deadline', '')})" if task.get("deadline") else ""
            created_at = f" (Created: {task['created_at']})" if task.get("created_at") else ""
            note = f" (Note: {task.get('note', '')})" if task.get("note") else ""
            print(f"{index}. {task['Title']} ---> {status}{deadline}{created_at}{note}")

def add_task(tasks):
    Title = input("Enter the task name: ").strip() 
    deadline = input("Enter the deadline (optional, YYYY-MM-DD): ").strip()
    if deadline:
        try:
            date.fromisoformat(deadline)
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return
    note = input("Enter a note (optional): ").strip()
    if not Title:
        print("Task name cannot be empty.")
        return
    tasks.append({
        "Title": Title,
        "completed": False,
        "deadline": deadline,
        "created_at": date.today().isoformat(), # date & time
        "note": note
    })
    save_tasks(tasks)
    print(f"Task added successfully.")

def complete_task(tasks):
    view_tasks(tasks)
    if not tasks:
        return
    try:
        task_index = int(input("Enter the task number to mark as completed: ")) - 1
        if 0 <= task_index < len(tasks):
            tasks[task_index]["completed"] = True
            save_tasks(tasks)
            print(f"Task '{tasks[task_index]['Title']}' marked as completed.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")

def delete_task(tasks):
    view_tasks(tasks)
    if not tasks:
        return
    try:
        task_index = int(input("Enter the task number to delete: ")) - 1
        if 0 <= task_index < len(tasks):
            deleted_task = tasks.pop(task_index)
            save_tasks(tasks)
            print(f"Task '{deleted_task['Title']}' deleted successfully.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")

def main():
    tasks = load_tasks()
    while True:
        print("\n------ TO-DO LIST ------")
        print("1. View Tasks")
        print("2. Add Task")
        print("3. Complete Task")
        print("4. Delete Task")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ")
        if choice == "1":
            view_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            complete_task(tasks)
        elif choice == "4":
            delete_task(tasks)
        elif choice == "5":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")
if __name__ == "__main__":
    main()
