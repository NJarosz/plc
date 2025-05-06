import tkinter as tk
from tkinter import ttk, messagebox
import json
#from config import EMPLOYEE_INFO_FILE, PRODUCTION_INFO_FILE, TOTAL_COUNT_FILE, PI_NUM

class PLCGui:
    def __init__(self, root):
        self.root = root
        self.root.title("PLC Configuration")
        self.root.geometry("400x600")

        # Notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True)

        # Tabs
        self.sequence_frame = ttk.Frame(self.notebook)
        self.prod_frame = ttk.Frame(self.notebook)
        self.emp_frame = ttk.Frame(self.notebook)
        self.count_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.sequence_frame, text="Sequence")
        self.notebook.add(self.prod_frame, text="Production")
        self.notebook.add(self.emp_frame, text="Employees")
        self.notebook.add(self.count_frame, text="Total Count")

        # Sequence Tab
        self.seq_label = ttk.Label(self.sequence_frame, text="Sequence (e.g., '1-on,1'):")
        self.seq_label.pack(pady=5)
        self.seq_text = tk.Text(self.sequence_frame, height=10, width=40)
        self.seq_text.pack(pady=5)
        self.load_sequence()

        # Production Tab
        ttk.Label(self.prod_frame, text="Part Number:").pack(pady=5)
        self.part_entry = ttk.Entry(self.prod_frame)
        self.part_entry.pack(pady=5)
        ttk.Label(self.prod_frame, text="Machine Number:").pack(pady=5)
        self.mach_entry = ttk.Entry(self.prod_frame)
        self.mach_entry.pack(pady=5)
        ttk.Label(self.prod_frame, text="Count Goal:").pack(pady=5)
        self.count_goal_entry = ttk.Entry(self.prod_frame)
        self.count_goal_entry.pack(pady=5)
        self.load_production()

        # Employee Tab
        ttk.Label(self.emp_frame, text="ID,Name (one per line):").pack(pady=5)
        self.emp_text = tk.Text(self.emp_frame, height=10, width=40)
        self.emp_text.pack(pady=5)
        self.load_employees()

        # Total Count Tab
        ttk.Label(self.count_frame, text="Total Count:").pack(pady=5)
        self.count_entry = ttk.Entry(self.count_frame)
        self.count_entry.pack(pady=5)
        self.load_total_count()

        # Save Button
        self.save_button = ttk.Button(root, text="Save Changes", command=self.save_all)
        self.save_button.pack(pady=10)

    def load_sequence(self):
        pass
        # try:
        #     with open("/home/pi/Documents/sequence.txt", "r") as f:  # Adjust path if needed
        #         self.seq_text.insert(tk.END, f.read())
        # except FileNotFoundError:
        #     self.seq_text.insert(tk.END, "1-on,1\n2-tmr,0.5\n3-off,1")

    def load_production(self):
        pass
        # try:
        #     with open(PRODUCTION_INFO_FILE, "r") as f:
        #         for line in f:
        #             if "#" not in line and line.strip():
        #                 key, value = line.strip().split(",")
        #                 if key == "part":
        #                     self.part_entry.insert(0, value)
        #                 elif key == "mach":
        #                     self.mach_entry.insert(0, value)
        #                 elif key == "count_goal":
        #                     self.count_goal_entry.insert(0, value)
        # except FileNotFoundError:
        #     self.part_entry.insert(0, "ABC123")
        #     self.mach_entry.insert(0, "M1")
        #     self.count_goal_entry.insert(0, "10")

    def load_employees(self):
        pass
        # try:
        #     with open(EMPLOYEE_INFO_FILE, "r") as f:
        #         self.emp_text.insert(tk.END, f.read())
        # except FileNotFoundError:
        #     self.emp_text.insert(tk.END, "123,john\n456,jane")

    def load_total_count(self):
        pass
        # try:
        #     with open(TOTAL_COUNT_FILE, "r") as f:
        #         self.count_entry.insert(0, f.read().strip())
        # except FileNotFoundError:
        #     self.count_entry.insert(0, "0")

    def save_all(self):
        pass
        # # Sequence
        # with open("/home/pi/Documents/sequence.txt", "w") as f:
        #     f.write(self.seq_text.get("1.0", tk.END).strip())
        # # Production
        # with open(PRODUCTION_INFO_FILE, "w") as f:
        #     f.write(f"part,{self.part_entry.get()}\n")
        #     f.write(f"mach,{self.mach_entry.get()}\n")
        #     f.write(f"count_goal,{self.count_goal_entry.get()}\n")
        # # Employees
        # with open(EMPLOYEE_INFO_FILE, "w") as f:
        #     f.write(self.emp_text.get("1.0", tk.END).strip())
        # # Total Count
        # with open(TOTAL_COUNT_FILE, "w") as f:
        #     f.write(self.count_entry.get())
        # messagebox.showinfo("Success", "All changes saved!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PLCGui(root)
    root.mainloop()