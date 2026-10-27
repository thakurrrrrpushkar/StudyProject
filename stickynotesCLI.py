import json
import os
FILENAME = "sticky_notes.json"
MAX_NOTES = 5
def load_notes():
    if os.path.exists(FILENAME):
        try:
            with open(FILENAME, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []
def save_notes(notes):
    with open(FILENAME, "w") as f:
        json.dump(notes, f, indent=4)
def view_notes(notes):
    if not notes:
        print("\nNo sticky notes found. Your board is empty.")
        return
    print("\n--- YOUR STICKY NOTES ---")
    for i, note in enumerate(notes, 1):
        print(f"[{i}] {note}")
    print(f"--------------------------")
    print(f"Total Notes: {len(notes)}/{MAX_NOTES}\n")
def add_note(notes):
    if len(notes) >= MAX_NOTES:
        print(f"\nLimit Reached: You can only have a maximum of {MAX_NOTES} sticky notes. Delete one to add a new note.")
        return notes
    content = input("\nEnter the content for your sticky note: ").strip()
    if content:
        notes.append(content)
        save_notes(notes)
        print("\nSticky note added successfully!")
    else:
        print("\nNote cannot be empty.")
    return notes
def edit_note(notes):
    view_notes(notes)
    if not notes:
        return notes
    try:
        choice = int(input("Enter the note number you want to edit: "))
        if 1 <= choice <= len(notes):
            new_content = input(f"Enter new content for note {choice}: ").strip()
            if new_content:
                notes[choice - 1] = new_content
                save_notes(notes)
                print("\nSticky note updated successfully!")
            else:
                print("\nNote content cannot be empty.")
        else:
            print("\nInvalid note number.")
    except ValueError:
        print("\nPlease enter a valid number.")
    return notes
def delete_note(notes):
    view_notes(notes)
    if not notes:
        return notes
    try:
        choice = int(input("Enter the note number you want to delete: "))
        if 1 <= choice <= len(notes):
            removed = notes.pop(choice - 1)
            save_notes(notes)
            print(f"\nSticky note {choice} deleted successfully!")
        else:
            print("\nInvalid note number.")
    except ValueError:
        print("\nPlease enter a valid number.")
    return notes
def main():
    notes = load_notes()
    while True:
        print("\n=== STICKY NOTES CLI ===")
        print("1. View Notes")
        print("2. Add Note")
        print("3. Edit Note")
        print("4. Delete Note")
        print("5. Exit")
        choice = input("Choose an option (1-5): ").strip()
        if choice == '1':
            view_notes(notes)
        elif choice == '2':
            notes = add_note(notes)
        elif choice == '3':
            notes = edit_note(notes)
        elif choice == '4':
            notes = delete_note(notes)
        elif choice == '5':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please select between 1 and 5.")
if __name__ == "__main__":
    main()
