import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import schedule
import time
import webbrowser
import pyautogui
import threading
import json
import os
import platform
SCHEDULE_FILE = 'meet_schedule.json'
ICON_BASE64 = """
R0lGODlhIAAgAPAAAAAAAAAAACH5BAEAAAAALAAAAAAgACAAAAO8jI+py+0Po5y02ouz3rz7D4bi
SJbmiabqyrbuC8fyTNf2jef6zvf+DwwKh8Si8YhMKpfMpvMJjUqn1Kr1is1qt9yu9wsOi8fksvmM
TqvX7Lb7DY/L5/S6/Y7P6/f8vv8PGCg4SFhoeIiYqLjI2Oj4CBkpOUlZaXmJmam5yZgZ6goaKjpK
Wmp6ipqqusra6voKGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/AwdLT1NXW19jZ2tvc3d
7f4OHi4+Tl5ufo6err7O3u7+Dh8vP09fb3+Pn6+/z9/v/wADs=
"""
class MeetSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Meet Auto-Joiner")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        try:
            icon = PhotoImage(data=ICON_BASE64)
            self.root.iconphoto(False, icon)
        except tk.TclError:
            print("Could not load application icon.")
        self.schedule_list = self.load_schedule()
        self.setup_styles()
        self.create_widgets()
        self.populate_schedule_tree()
        self.setup_and_run_scheduler()
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=5)
        style.configure("Treeview", rowheight=25, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        style.map("TButton",
            foreground=[('active', 'white'), ('!disabled', 'white')],
            background=[('active', '#0052cc'), ('!disabled', '#0078d4')])
        style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="#333")
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        input_frame = ttk.Frame(main_frame, padding="10")
        input_frame.pack(fill=tk.X, pady=5)
        input_frame.columnconfigure(1, weight=1)
        ttk.Label(input_frame, text="Day:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.day_var = tk.StringVar()
        self.day_dropdown = ttk.Combobox(input_frame, textvariable=self.day_var,
            values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            state="readonly")
        self.day_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.day_dropdown.set("Monday")
        ttk.Label(input_frame, text="Time (24h HH:MM):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.time_entry = ttk.Entry(input_frame)
        self.time_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(input_frame, text="Meet URL:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.url_entry = ttk.Entry(input_frame)
        self.url_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(input_frame, text="Duration (mins):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.duration_entry = ttk.Entry(input_frame)
        self.duration_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        self.add_button = ttk.Button(button_frame, text="Add Class to Schedule", command=self.add_class)
        self.add_button.grid(row=0, column=0, padx=5, sticky="ew")
        self.remove_button = ttk.Button(button_frame, text="Remove Selected Class", command=self.remove_class)
        self.remove_button.grid(row=0, column=1, padx=5, sticky="ew")
        schedule_frame = ttk.Frame(main_frame)
        schedule_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        cols = ("Day", "Time", "URL", "Duration")
        self.schedule_tree = ttk.Treeview(schedule_frame, columns=cols, show='headings')
        for col in cols:
            self.schedule_tree.heading(col, text=col)
        self.schedule_tree.column("Day", width=100, anchor=tk.W)
        self.schedule_tree.column("Time", width=80, anchor=tk.CENTER)
        self.schedule_tree.column("URL", width=300, anchor=tk.W)
        self.schedule_tree.column("Duration", width=100, anchor=tk.CENTER)
        self.schedule_tree.pack(fill=tk.BOTH, expand=True)
        self.status_var = tk.StringVar()
        self.status_var.set("Scheduler is running. Add your classes.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, style="Status.TLabel", anchor="w", padding=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    def add_class(self):
        day = self.day_var.get()
        time_str = self.time_entry.get()
        url = self.url_entry.get()
        duration_str = self.duration_entry.get()
        if not (day and time_str and url and duration_str):
            messagebox.showerror("Error", "All fields are required.")
            return
        try:
            time.strptime(time_str, '%H:%M')
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Please use HH:MM (24-hour).")
            return
        try:
            duration = int(duration_str)
            if duration <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Duration must be a positive number of minutes.")
            return
        class_details = {"day": day, "time": time_str, "url": url, "duration": duration}
        self.schedule_list.append(class_details)
        self.save_schedule()
        self.populate_schedule_tree()
        self.update_scheduler()
        self.time_entry.delete(0, tk.END)
        self.url_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)
        self.status_var.set(f"Added class for {day} at {time_str}.")
    def remove_class(self):
        selected_item = self.schedule_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a class to remove.")
            return
        selected_index = self.schedule_tree.index(selected_item[0])
        del self.schedule_list[selected_index]
        self.save_schedule()
        self.populate_schedule_tree()
        self.update_scheduler()
        self.status_var.set("Removed selected class from the schedule.")
    def populate_schedule_tree(self):
        for i in self.schedule_tree.get_children():
            self.schedule_tree.delete(i)
        for item in self.schedule_list:
            self.schedule_tree.insert("", "end", values=(item['day'], item['time'], item['url'], f"{item['duration']} mins"))
    def load_schedule(self):
        if os.path.exists(SCHEDULE_FILE):
            try:
                with open(SCHEDULE_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                messagebox.showerror("Error", f"Could not read or parse {SCHEDULE_FILE}. Starting with an empty schedule.")
                return []
        return []
    def save_schedule(self):
        try:
            with open(SCHEDULE_FILE, 'w') as f:
                json.dump(self.schedule_list, f, indent=4)
        except IOError:
            messagebox.showerror("Error", f"Could not save schedule to {SCHEDULE_FILE}.")
    def update_scheduler(self):
        schedule.clear()
        for job_details in self.schedule_list:
            day = job_details['day'].lower()
            job_func = getattr(schedule.every(), day)
            job_func.at(job_details['time']).do(self.join_and_leave_meet, job_details['url'], job_details['duration'])
        print("Scheduler updated with current class list.")
        self.status_var.set("Scheduler reloaded with the updated class list.")
    def join_and_leave_meet(self, url, duration):
        try:
            self.status_var.set(f"Attempting to join: {url}")
            print(f"Joining Google Meet at {url}...")
            webbrowser.open(url, new=2)
            time.sleep(15)
            self.status_var.set("Turning off camera and microphone...")
            print("Turning off camera (Ctrl+E) and microphone (Ctrl+D)...")
            modifier_key = 'command' if platform.system() == 'Darwin' else 'ctrl'
            pyautogui.hotkey(modifier_key, 'd')
            time.sleep(1)
            pyautogui.hotkey(modifier_key, 'e')
            time.sleep(1)
            for attempt in range(3):
                try:
                    join_button_location = pyautogui.locateCenterOnScreen('join_button.png', confidence=0.9)
                    if join_button_location:
                        pyautogui.click(join_button_location)
                        print("Successfully clicked the 'Join now' button.")
                        self.status_var.set(f"Successfully joined. Class duration: {duration} mins.")
                        break
                    else:
                         print(f"Attempt {attempt+1}: 'join_button.png' not found. Retrying...")
                         time.sleep(5)
                except Exception as e:
                    print(f"Error locating screenshot: {e}. Ensure 'join_button.png' exists.")
            else:
                print("Could not find 'Join now' button via screenshot after several attempts.")
                self.status_var.set("Failed to find 'Join Now' button. Please check the browser.")
            time.sleep(duration * 60)
            print("Class time is over. Leaving the call...")
            self.status_var.set("Class time over. Leaving call...")
            pyautogui.hotkey(modifier_key, 'w')
            print("Successfully left the call.")
            self.status_var.set("Scheduler is running. Waiting for next class.")
        except Exception as e:
            print(f"An error occurred during the join/leave process: {e}")
            self.status_var.set(f"An error occurred. Check logs.")
    def scheduler_thread_func(self):
        self.update_scheduler()
        while not self.stop_scheduler.is_set():
            next_run = schedule.idle_seconds()
            if next_run is not None and next_run > 0:
                time.sleep(min(next_run, 1))
            schedule.run_pending()
        print("Scheduler thread has stopped.")
    def setup_and_run_scheduler(self):
        self.stop_scheduler = threading.Event()
        self.scheduler_thread = threading.Thread(target=self.scheduler_thread_func, daemon=True)
        self.scheduler_thread.start()
        print("Scheduler background thread started.")
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to exit? The scheduler will stop."):
            self.stop_scheduler.set()
            self.root.destroy()
if __name__ == "__main__":
    app_root = tk.Tk()
    app = MeetSchedulerApp(app_root)
    app_root.mainloop()
