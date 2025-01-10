import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import threading
import json
import os

# default subject status
subjects = {
    "Bangla": {"chapters": 6, "completed": 20, "difficulty": "Quite difficult", "exam_date": datetime.date(2024, 11, 19)},
    "History and Social Science": {"chapters": 6, "completed": 60, "difficulty": "Quite difficult", "exam_date": datetime.date(2024, 11, 24)},
    "Science": {"chapters": 8, "completed": 30, "difficulty": "Really difficult", "exam_date": datetime.date(2024, 11, 26)},
    "Religion": {"chapters": 6, "completed": 40, "difficulty": "Somewhat difficult", "exam_date": datetime.date(2024, 11, 28)},
    "English": {"chapters": "Parts", "completed": 80, "difficulty": "Easy", "exam_date": datetime.date(2024, 12, 1)},
    "Digital Technology": {"chapters": 5, "completed": 60, "difficulty": "Not that difficult", "exam_date": datetime.date(2024, 12, 4)},
    "Math": {"chapters": 6, "completed": 70, "difficulty": "Not that difficult", "exam_date": datetime.date(2024, 12, 8)}
}

# create log file path
study_log_file = "study_log.json"

# open ager log file
def load_study_logs():
    if os.path.exists(study_log_file):
        with open(study_log_file, 'r') as file:
            return json.load(file)
    return []

# save recent study to logs
def save_study_logs(logs):
    with open(study_log_file, 'w') as file:
        json.dump(logs, file)

# which sub to study
def select_subject():
    today = datetime.date.today()
    prioritized_subjects = sorted(
        subjects.items(),
        key=lambda item: (
            (item[1]['exam_date'] - today).days,  # days until exam
            item[1]['completed'],  # percent completed
            item[1]['difficulty']  # difficulty (choose by the user)
        )
    )
    subject_to_study = prioritized_subjects[0][0]
    return subject_to_study

# calculate prep time
def days_until_exam(exam_date):
    today = datetime.date.today()
    return (exam_date - today).days

class StudyPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Planner")
        self.root.geometry("800x600")

        self.reminder_timer = None
        self.reminder_active = False  

        self.study_logs = load_study_logs()

        
        self.setup_main_gui()

        
        self.set_study_reminder()

        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_main_gui(self):
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        
        self.canvas = tk.Canvas(main_frame)
        self.scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        
        self.selector_frame = ttk.LabelFrame(self.scrollable_frame, text="Subject Selector", padding=10)
        self.selector_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.progress_frame = ttk.LabelFrame(self.scrollable_frame, text="Progress Overview", padding=10)
        self.progress_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        
        self.log_update_frame = ttk.Frame(self.scrollable_frame)
        self.log_update_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.log_frame = ttk.LabelFrame(self.log_update_frame, text="Study Session Log", padding=10)
        self.log_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.update_frame = ttk.LabelFrame(self.log_update_frame, text="Update Progress", padding=10)
        self.update_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        
        self.scrollable_frame.grid_rowconfigure(0, weight=1)
        self.scrollable_frame.grid_rowconfigure(1, weight=1)

        #run functions
        self.show_subject_selector()
        self.show_progress_overview()
        self.show_log_session()
        self.show_update_progress()

    def show_subject_selector(self):
        for widget in self.selector_frame.winfo_children():
            widget.destroy()

        subject_to_study = select_subject()
        ttk.Label(self.selector_frame, text=f"Suggested Subject: {subject_to_study}").grid(row=0, column=0, pady=5)

        study_button = ttk.Button(
            self.selector_frame,
            text="Start Studying",
            command=lambda: self.start_study_session(subject_to_study)
        )
        study_button.grid(row=1, column=0, pady=5)

        row = 2
        for subject, info in subjects.items():
            days_left = days_until_exam(info['exam_date'])
            subject_label = ttk.Label(
                self.selector_frame,
                text=f"{subject}: {days_left} days until exam",
                font=("JetBrains Mono", 10, "bold") if days_left <= 7 else ("JetBrains Mono", 10)
            )
            if days_left <= 7:
                subject_label.config(foreground="red")
            subject_label.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            row += 1

    def start_study_session(self, subject):
        messagebox.showinfo("Start Studying", f"You selected to study {subject}. Good luck!")

    def show_progress_overview(self):
        for widget in self.progress_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.progress_frame, text="Subject Progress Overview:").grid(row=0, column=0, pady=5)
        for index, (subject, info) in enumerate(subjects.items()):
            progress_label = ttk.Label(
                self.progress_frame,
                text=f"{subject}: {info['completed']}% completed",
                font=("JetBrains Mono", 10)
            )
            progress_label.grid(row=index + 1, column=0, sticky="w", padx=5, pady=2)

        # display recent updates
        if self.study_logs:
            ttk.Label(self.progress_frame, text="Recent Study Logs:").grid(row=len(subjects) + 1, column=0, pady=5)
            for index, log in enumerate(self.study_logs[-5:]):  # Show last 5 logs
                log_text = f"{log['date']}: {log['subject']} - {log['completed']}% completed"
                ttk.Label(self.progress_frame, text=log_text).grid(row=len(subjects) + 2 + index, column=0, sticky="w", padx=5, pady=2)
        else:
            ttk.Label(self.progress_frame, text="No recent study logs available.").grid(row=len(subjects) + 1, column=0, padx=5, pady=5)

    def show_update_progress(self):
        for widget in self.update_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.update_frame, text="Select Subject:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        subject_var = tk.StringVar()
        subject_dropdown = ttk.Combobox(self.update_frame, textvariable=subject_var, values=list(subjects.keys()))
        subject_dropdown.grid(row=0, column=1, padx=5)

        ttk.Label(self.update_frame, text="Update Completion (%):").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        completion_entry = ttk.Entry(self.update_frame)
        completion_entry.grid(row=1, column=1, padx=5)

        update_button = ttk.Button(self.update_frame, text="Update", command=lambda: self.update_progress(subject_var.get(), completion_entry.get()))
        update_button.grid(row=2, column=0, columnspan=2, pady=5)

    def update_progress(self, subject, completion):
        try:
            completion = int(completion)
            if 0 <= completion <= 100:
                subjects[subject]['completed'] = completion
                self.show_progress_overview()  
                self.show_subject_selector()  
                save_study_logs(self.study_logs)  
            else:
                messagebox.showerror("Invalid Input", "Please enter a value between 0 and 100.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")

    def show_log_session(self):
        for widget in self.log_frame.winfo_children():
            widget.destroy()

        
        add_log_frame = ttk.Frame(self.log_frame)
        add_log_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        subject_var = tk.StringVar()
        subject_dropdown = ttk.Combobox(add_log_frame, textvariable=subject_var, values=list(subjects.keys()), state="readonly")
        subject_dropdown.grid(row=0, column=0, padx=5)

        note_entry = ttk.Entry(add_log_frame)
        note_entry.grid(row=0, column=1, padx=5)

        add_log_button = ttk.Button(add_log_frame, text="Add Log", command=lambda: self.add_log(subject_var.get(), note_entry.get()))
        add_log_button.grid(row=0, column=2, padx=5)

        if self.study_logs:
            for index, log in enumerate(self.study_logs):
                log_text = f"{log['date']}: {log['subject']} - {log['completed']}% completed"
                ttk.Label(self.log_frame, text=log_text).grid(row=index + 1, column=0, sticky="w", padx=5, pady=2)
                remove_button = ttk.Button(self.log_frame, text="Remove", command=lambda idx=index: self.remove_log_entry(idx))
                remove_button.grid(row=index + 1, column=1, padx=5, pady=2)
        else:
            ttk.Label(self.log_frame, text="No study logs available.").grid(row=1, column=0, padx=5, pady=5)

    def add_log(self, subject, notes):
        if subject and notes:
            log_entry = {"subject": subject, "completed": subjects[subject]['completed'], "notes": notes, "date": str(datetime.date.today())}
            self.study_logs.append(log_entry)
            save_study_logs(self.study_logs)  
            self.show_log_session()  
        else:
            messagebox.showerror("Invalid Input", "Please select a subject and enter notes.")

    def remove_log_entry(self, index):
        self.study_logs.pop(index)  
        save_study_logs(self.study_logs)  
        self.show_log_session()  

    def set_study_reminder(self):
        reminder_interval = 1800  

        def remind():
            if self.reminder_active:
                messagebox.showinfo("Study Reminder", "Time to study!")
            self.reminder_active = True
            self.reminder_timer = threading.Timer(reminder_interval, remind)
            self.reminder_timer.start()

        if not self.reminder_active:
            self.reminder_timer = threading.Timer(reminder_interval, remind)
            self.reminder_timer.start()

    def on_close(self):
        if self.reminder_timer:
            self.reminder_timer.cancel()
        self.root.destroy()

# run app
if __name__ == "__main__":
    root = tk.Tk()
    app = StudyPlannerApp(root)
    root.mainloop()