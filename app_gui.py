import json
import os
import schedule
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

DATA_DIR = "data"
MEDICINES_FILE = os.path.join(DATA_DIR, "medicines.json")
LOGS_FILE = os.path.join(DATA_DIR, "logs.json")


def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_medicines():
    return load_json(MEDICINES_FILE, [])


def save_medicines(medicines):
    save_json(MEDICINES_FILE, medicines)


def load_logs():
    return load_json(LOGS_FILE, [])


def save_logs(logs):
    save_logs.logs_cache = logs  # cache for quick access if needed
    save_json(LOGS_FILE, logs)


def validate_time_str(time_str):
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False


def log_dose(medicine_name, scheduled_time, taken):
    logs = load_logs()
    entry = {
        "medicine": medicine_name,
        "scheduled_time": scheduled_time,
        "responded_at": datetime.now().isoformat(timespec="seconds"),
        "taken": taken,
    }
    logs.append(entry)
    save_logs(logs)


def reminder_job(medicine_name, dose, instructions, time_str):
    # Build scheduled datetime string (today's date + time)
    scheduled_dt = datetime.now().strftime("%Y-%m-%d ") + time_str

    msg = (
        f"Medicine : {medicine_name}\n"
        f"Dosage   : {dose}\n"
        f"When     : {time_str} (now)\n"
        f"Note     : {instructions}\n\n"
        "Did you take it?"
    )
    taken = messagebox.askyesno("Medicine Reminder", msg)
    log_dose(medicine_name, scheduled_dt, taken)


class MedicineReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medicine Reminder App")
        self.root.geometry("800x450")
        self.root.minsize(700, 400)

        ensure_data_dir()

        # Configure a slightly more modern ttk theme
        style = ttk.Style()
        try:
            # Use 'clam' for a cleaner look if available
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TLabel", padding=2)
        style.configure("TButton", padding=4)
        style.configure("Treeview", rowheight=22)

        self.medicines = load_medicines()
        self.schedule_running = False

        self.create_widgets()
        self.populate_medicines_list()

    def create_widgets(self):
        # Top frame for form
        form_frame = ttk.LabelFrame(self.root, text="Add Medicine")
        form_frame.pack(fill="x", padx=10, pady=10)

        # Grid weight to stretch nicely
        for i in range(4):
            form_frame.columnconfigure(i, weight=1)

        # Name
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5
        )

        # Dose
        ttk.Label(form_frame, text="Dosage:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.dose_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.dose_var).grid(
            row=0, column=3, sticky="ew", padx=5, pady=5
        )

        # Instructions
        ttk.Label(form_frame, text="Instructions:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.instructions_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.instructions_var).grid(
            row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=5
        )

        # Times
        ttk.Label(form_frame, text="Times (HH:MM, comma separated):").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.times_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.times_var).grid(
            row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=5
        )

        add_btn = ttk.Button(form_frame, text="Add Medicine", command=self.add_medicine)
        add_btn.grid(row=2, column=3, padx=5, pady=5, sticky="e")

        # Middle frame for list
        list_frame = ttk.LabelFrame(self.root, text="Medicines")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "name", "dose", "times", "instructions")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("dose", text="Dosage")
        self.tree.heading("times", text="Times")
        self.tree.heading("instructions", text="Instructions")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=150)
        self.tree.column("dose", width=80, anchor="center")
        self.tree.column("times", width=180)
        self.tree.column("instructions", width=250)

        self.tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)

        # Bottom frame for buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Show Dose History", command=self.show_logs_window).pack(side="left", padx=5)

        self.start_btn = ttk.Button(btn_frame, text="Start Reminders", command=self.start_reminders)
        self.start_btn.pack(side="right", padx=5)

        self.status_label = ttk.Label(btn_frame, text="Status: Stopped")
        self.status_label.pack(side="right", padx=5)

    def populate_medicines_list(self):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        for med in self.medicines:
            times_str = ", ".join(med.get("times", []))
            self.tree.insert(
                "",
                "end",
                values=(
                    med["id"],
                    med["name"],
                    med["dose"],
                    times_str,
                    med["instructions"],
                ),
            )

    def add_medicine(self):
        name = self.name_var.get().strip()
        dose = self.dose_var.get().strip() or "N/A"
        instructions = self.instructions_var.get().strip() or "N/A"
        times_input = self.times_var.get().strip()

        if not name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return

        if not times_input:
            messagebox.showerror("Error", "Please enter at least one time.")
            return

        times_raw = [t.strip() for t in times_input.split(",") if t.strip()]
        times = []
        for t in times_raw:
            if not validate_time_str(t):
                messagebox.showerror("Error", f"Invalid time format: {t}\nUse HH:MM in 24-hour format.")
                return
            times.append(t)

        med_id = len(self.medicines) + 1
        med = {
            "id": med_id,
            "name": name,
            "dose": dose,
            "instructions": instructions,
            "times": times,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        self.medicines.append(med)
        save_medicines(self.medicines)

        # Clear form
        self.name_var.set("")
        self.dose_var.set("")
        self.instructions_var.set("")
        self.times_var.set("")

        self.populate_medicines_list()
        messagebox.showinfo("Saved", f"Medicine '{name}' added with times: {', '.join(times)}")

        # If schedule is running, reschedule with new data
        if self.schedule_running:
            self.schedule_all_medicines()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a medicine to delete.")
            return

        item = selected[0]
        values = self.tree.item(item, "values")
        med_id = int(values[0])

        confirm = messagebox.askyesno("Confirm delete", f"Delete medicine ID {med_id}?")
        if not confirm:
            return

        self.medicines = [m for m in self.medicines if m["id"] != med_id]
        # Reassign IDs
        for idx, med in enumerate(self.medicines, start=1):
            med["id"] = idx
        save_medicines(self.medicines)
        self.populate_medicines_list()

        messagebox.showinfo("Deleted", f"Medicine ID {med_id} deleted.")

        if self.schedule_running:
            self.schedule_all_medicines()

    def schedule_all_medicines(self):
        schedule.clear()
        if not self.medicines:
            return False
        for med in self.medicines:
            for t in med.get("times", []):
                schedule.every().day.at(t).do(
                    reminder_job,
                    medicine_name=med["name"],
                    dose=med["dose"],
                    instructions=med["instructions"],
                    time_str=t,
                )
        return True

    def start_reminders(self):
        if not self.schedule_all_medicines():
            messagebox.showwarning("No medicines", "Add at least one medicine first.")
            return

        if not self.schedule_running:
            self.schedule_running = True
            self.status_label.config(text="Status: Running")
            self.start_btn.config(state="disabled")  # keep simple: no stop button
            self.run_schedule_loop()

    def run_schedule_loop(self):
        if not self.schedule_running:
            return
        schedule.run_pending()
        # call again after 1 second
        self.root.after(1000, self.run_schedule_loop)

    def show_logs_window(self):
        logs = load_logs()
        if not logs:
            messagebox.showinfo("Dose History", "No dose logs yet.")
            return

        win = tk.Toplevel(self.root)
        win.title("Dose History")
        win.geometry("520x320")

        columns = ("time", "medicine", "status")
        tree = ttk.Treeview(win, columns=columns, show="headings", height=12)
        tree.heading("time", text="Scheduled Time")
        tree.heading("medicine", text="Medicine")
        tree.heading("status", text="Status")

        tree.column("time", width=180)
        tree.column("medicine", width=200)
        tree.column("status", width=80, anchor="center")

        for entry in logs:
            status = "Taken" if entry["taken"] else "Missed"
            tree.insert("", "end", values=(entry["scheduled_time"], entry["medicine"], status))

        tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = MedicineReminderApp(root)
    root.mainloop()
