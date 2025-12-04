# Medicine Reminder App (Python + Tkinter)

A simple **desktop Medicine Reminder App** built with Python, Tkinter (GUI), and the `schedule` library.

The app lets you:

- Add medicines with name, dosage, instructions, and one or more times per day
- See all medicines in a table
- Receive pop-up reminders at the scheduled times
- Mark doses as taken/missed (via Yes/No)
- View dose history in a separate window
- Data is stored locally in simple JSON files

This is a great beginner-friendly project that demonstrates:

- Basic GUI development with Tkinter + ttk
- Scheduling background jobs with `schedule`
- Working with JSON for persistent storage
- Clean separation of UI and logic

---

## Features

- 🧾 Add multiple medicines with:
  - Name
  - Dosage (e.g. `500mg`)
  - Instructions (e.g. `after food`)
  - Times in 24-hour format (e.g. `08:00, 21:30`)
- 📋 View all medicines in a table
- 🗑️ Delete selected medicine
- ⏰ Start daily reminders (runs as long as the app window is open)
- ✅ Popup reminder dialog with "Yes / No"
- 📊 Dose history: see when a medicine was scheduled and whether it was taken or missed

> ⚠️ **Disclaimer:** This app is a simple reminder tool only. It should *not* be considered a medical device. Always follow your doctor's advice and double-check your medication.

---

## Tech Stack

- **Language:** Python 3
- **GUI:** Tkinter + ttk (modern themed widgets)
- **Scheduling:** [`schedule`](https://pypi.org/project/schedule/)
- **Storage:** Local JSON files (`data/medicines.json`, `data/logs.json`)

---

## Project Structure

```text
medicine-reminder-app/
│ app_gui.py          # Main Tkinter GUI application
│ requirements.txt    # Python dependencies
│ README.md           # Project documentation
│ .gitignore
└─data/
   ├─ medicines.json  # Created automatically on first run
   └─ logs.json       # Created automatically on first logged dose
```

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/medicine-reminder-app.git
cd medicine-reminder-app
```

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
# Activate it:
# On Windows:
venv\Scripts\activate
# On macOS / Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Tkinter usually comes pre-installed with Python (especially on Windows). If not, install it using your OS package manager.

---

## How to Run

From the project root:

```bash
python app_gui.py
```

The main window will open with:

- A form at the top to add a new medicine
- A table in the middle with all medicines
- Buttons at the bottom for:
  - Delete Selected
  - Show Dose History
  - Start Reminders

> 🔁 **Important:** Reminders only work while the app is running, so keep the window open.

---

## How to Use

### 1. Add a medicine

Fill the **"Add Medicine"** form at the top:

- **Name** – e.g. `Paracetamol`
- **Dosage** – e.g. `500mg`
- **Instructions** – e.g. `After food`
- **Times** – one or more times in 24-hour format, comma-separated  
  Example:  
  - `08:00`  
  - `09:00, 21:30`

Click **"Add Medicine"**.

The medicine will appear in the table below.

---

### 2. Start reminders

1. Add at least one medicine.
2. Click **"Start Reminders"**.
3. Status label will change to **"Status: Running"**.
4. When the current time matches any of the scheduled times:
   - A popup window appears showing:
     - Medicine name
     - Dosage
     - Time
     - Instructions
   - You will be asked: **"Did you take it?"**
   - Click **Yes** or **No**.
5. Your response is stored in the dose history JSON file.

> Tip: For testing, set a time 1–2 minutes from your current time.

---

### 3. View dose history

Click **"Show Dose History"** at the bottom:

- A new window opens
- Shows a table with:
  - Scheduled time (date + time)
  - Medicine name
  - Status: **Taken** / **Missed**

---

### 4. Delete a medicine

1. Select a row in the medicines table.
2. Click **"Delete Selected"**.
3. Confirm deletion.

The IDs are automatically re-assigned after deletion.

---

## Future Enhancements (Ideas)

You can extend this project with:

- Different schedules (specific days of week, end dates)
- System tray integration
- Real OS notifications (e.g. `plyer`)
- Export dose history as CSV
- Multi-user / profiles (e.g. family members)
- Packaging as an executable (using PyInstaller) for non-technical users

---

## License

Feel free to use, modify, and share this project in your portfolio or as a learning resource.
