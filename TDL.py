import json
import os
from datetime import date

FILE_NAME = "tasks.json"
def load_tasks():
    if not os.path.exists(FILE_NAME):
        return [] 
    try :
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the tasks file.")
        return []
    
def save_tasks(tasks):
    with open(FILE_NAME, "w") as file:   
        json.dump(tasks, file, indent=4) 

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
