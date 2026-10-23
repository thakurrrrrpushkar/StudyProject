import json
import os
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
def view_tasks(tasks):
    if not tasks:
        print("No tasks found.")
    else:
        print("\n------ TASKS ------")
        for index, task in enumerate(tasks, start=1):
            status = "Done" if task["completed"] else "Pending"
            print(f"{index}. {task['Title']} ---> {status}") 
def add_task(tasks):
    Title = input("Enter the task name: ").strip() 
    if not Title:
        print("Task name cannot be empty.")
        return
    tasks.append({"Title": Title, "completed": False})    
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
