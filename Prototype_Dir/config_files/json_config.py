import json
import sys
from config import EMPLOYEE_INFO_FILE, PRODUCTION_INFO_FILE, TOTAL_COUNT_FILE

def load_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    while True:
        print("\nPLC Config CLI")
        print("1. Edit Employees")
        print("2. Edit Production Info")
        print("3. Edit Total Count")
        print("4. Exit")
        choice = input("Select: ")

        if choice == "1":
            emps = load_json(EMPLOYEE_INFO_FILE)
            print("Current:", emps)
            id = input("Employee ID (or 'q' to quit): ")
            if id.lower() != 'q':
                name = input("Name: ")
                emps[id] = name
                save_json(EMPLOYEE_INFO_FILE, emps)
        elif choice == "2":
            prod = load_json(PRODUCTION_INFO_FILE)
            print("Current:", prod)
            prod["part"] = input("Part Number: ") or prod.get("part", "ABC123")
            prod["mach"] = input("Machine Number: ") or prod.get("mach", "M1")
            prod["count_goal"] = int(input("Count Goal: ") or prod.get("count_goal", 10))
            save_json(PRODUCTION_INFO_FILE, prod)
        elif choice == "3":
            count = load_json(TOTAL_COUNT_FILE)
            print("Current:", count)
            count["count"] = int(input("Total Count: ") or count.get("count", 0))
            save_json(TOTAL_COUNT_FILE, count)
        elif choice == "4":
            sys.exit(0)

if __name__ == "__main__":
    main()