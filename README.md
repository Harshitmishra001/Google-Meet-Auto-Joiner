# Google Meet Auto-Joiner

## 🚀 Overview

The **Google Meet Auto-Joiner** is a user-friendly desktop application designed to automate the process of joining and leaving Google Meet classes. If you find yourself forgetting to join online classes or want to ensure you're never marked absent, this tool is for you.

It provides a clean graphical user interface (UI) to manage a weekly schedule of your classes. Once set, the application runs quietly in the background, automatically opening your Google Meet links at the specified times, muting your microphone and camera, joining the call, and then closing the tab when the class duration is over.


---

## ✨ Features

- **Graphical User Interface:** An intuitive and professional-looking UI to easily add, view, and remove class schedules.
- **Weekly Scheduling:** Set up different Google Meet links for any day of the week and at any time.
- **Persistent Storage:** Your schedule is saved locally in a `meet_schedule.json` file, so you don't have to re-enter it every time you open the app.
- **Automated Joining:** The app automatically opens the correct Google Meet link in your default browser at the scheduled time.
- **Auto Mute/Camera Off:** Before joining the call, the application automatically toggles your microphone and camera off to ensure your privacy.
- **Automated Leaving:** The browser tab for the meeting is automatically closed after the specified class duration has passed.
- **Background Operation:** A multi-threaded design allows the scheduler to run in the background without freezing the application.
- **Cross-Platform:** Works on Windows, macOS, and Linux.

---

## 📋 Requirements

Before running the application, you need to have Python installed on your system. You will also need the following Python libraries:

- `schedule`
- `pyautogui`

---

## ⚙️ Setup & Installation

Follow these steps to get the application up and running:

**1. Save the Code:**
   - Save the main application code as a Python file (e.g., `meet_app.py`).

**2. Install Dependencies:**
   - Open your terminal or command prompt and run the following command to install the necessary libraries:
     ```bash
     pip install schedule pyautogui
     ```

---

## ▶️ How to Use

**1. Run the Application:**
   - Open your terminal or command prompt.
   - Navigate to the directory where you saved the files.
   - Run the script using:
     ```bash
     python meet_app.py
     ```

**2. Add a Class:**
   - Select the **Day** of the week from the dropdown menu.
   - Enter the **Time** in 24-hour `HH:MM` format (e.g., `14:30` for 2:30 PM).
   - Paste the full **Meet URL**.
   - Enter the **Duration** of the class in minutes.
   - Click the **"Add Class to Schedule"** button.

**3. Remove a Class:**
   - In the schedule view, click on the class you wish to remove.
   - Click the **"Remove Selected Class"** button.

**4. Let it Run:**
   - You can minimize the application window. The scheduler will continue to run in the background as long as the application is open. It will automatically perform its tasks at the scheduled times.

---

## 🛠️ How It Works

The application uses the `tkinter` library for its user interface. The `schedule` library is used to manage the timing of the jobs. When a scheduled time arrives, the `pyautogui` library takes control of the mouse and keyboard to perform the following actions:

1.  Opens the specified Google Meet URL in a new browser tab.
2.  Waits for the page to load.
3.  Presses the keyboard shortcuts (`Ctrl+D` and `Ctrl+E` or `Cmd+D` and `Cmd+E`) to mute the microphone and disable the camera.
4.  Locates the `join_button.png` on the screen and clicks it.
5.  After the specified duration, it presses `Ctrl+W` (or `Cmd+W`) to close the tab and leave the meeting.

---

## ⚠️ Disclaimer

This tool is intended for personal use to help manage online class attendance. Please use it responsibly. Using automation tools may be against the terms of service of your school or Google. The creator of this script is not responsible for any misuse or consequences that may arise from its use.
