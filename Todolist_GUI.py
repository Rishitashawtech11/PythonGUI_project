from tkinter import *
from tkinter import messagebox, ttk
from tkcalendar import Calendar
import json
import threading
import datetime
import time

def save_data(data):
    with open("tasks.json", "w") as f:
        json.dump(data, f, indent=4)

def load_data():
    for widget in task_container.winfo_children():
        widget.destroy()

    global task_names, done_vars, date_vals, time_vals
    task_names, done_vars, date_vals, time_vals = [], [], [], []

    try:
        with open("tasks.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    current_time = datetime.datetime.now()

    for i, item in enumerate(data):
        outer_box = Frame(task_container, bg="#EBF5FB")
        outer_box.pack(fill=X, pady=5)

        box = Frame(outer_box, bg="#FFFDD0", bd=2, relief=GROOVE, width=750, height=80)
        box.pack(anchor="center")
        box.pack_propagate(False)

        dt_str = item.get("datetime", "")
        try:
            deadline = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            remain = deadline - current_time
            if remain.total_seconds() > 0:
                hrs, rem = divmod(int(remain.total_seconds()), 3600)
                mins, secs = divmod(rem, 60)
                remain_text = f"{hrs}h {mins}m {secs}s left"
            else:
                remain_text = "Time passed"
        except Exception:
            remain_text = ""

        name_var = StringVar(value=item["task"])
        Entry(
            box,
            textvariable=name_var,
            width=28,
            font=("Segoe UI", 12, "bold"),
            justify="center",
            fg="#808000"
        ).grid(row=0, column=0, padx=20, pady=(10, 5))
        task_names.append(name_var)

        dt_box = Frame(box, bg="#FFFDD0")
        dt_box.grid(row=0, column=1, padx=20)

        date_text = dt_str.split()[0] if " " in dt_str else ""
        time_text = dt_str.split()[1] if " " in dt_str else ""

        d_var = StringVar(value=date_text)
        t_var = StringVar(value=time_text)

        Entry(dt_box, textvariable=d_var, width=12, font=("Segoe UI", 11, "bold"),
              justify="center", fg="black").grid(row=0, column=0, padx=3)

        Entry(dt_box, textvariable=t_var, width=8, font=("Segoe UI", 11, "bold"),
              justify="center", fg="black").grid(row=0, column=1, padx=3)

        date_vals.append(d_var)
        time_vals.append(t_var)

        Label(dt_box, text=remain_text, font=("Segoe UI", 10, "bold"),
              bg="#FFFDD0", fg="#FF69B4").grid(row=1, column=0, columnspan=2, pady=(3, 0))

        done = BooleanVar(value=item.get("read", False))
        Checkbutton(box, variable=done, bg="#FFFDD0").grid(row=0, column=2, padx=25)
        done_vars.append(done)

        Button(
            box, text="Delete", command=lambda x=i: delete_task(x),
            bg="#E74C3C", fg="white", font=("Segoe UI", 10, "bold"), width=8
        ).grid(row=0, column=3, padx=25)

    task_canvas.update_idletasks()
    task_canvas.config(scrollregion=task_canvas.bbox("all"))

def add_task():
    name = new_task.get().strip()
    selected_date = cal.get_date()
    hour = hour_val.get()
    minute = minute_val.get()

    if not name:
        messagebox.showwarning("Warning", "Please enter a task first!")
        return

    full_dt = f"{selected_date} {hour}:{minute}"
    new_entry = {"task": name, "datetime": full_dt, "read": False}

    try:
        with open("tasks.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(new_entry)
    save_data(data)
    new_task.set("")
    load_data()

def delete_task(i):
    try:
        with open("tasks.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    if 0 <= i < len(data):
        data.pop(i)
        save_data(data)
        load_data()

def save_all():
    try:
        with open("tasks.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    for i in range(len(data)):
        data[i]["task"] = task_names[i].get()
        data[i]["datetime"] = f"{date_vals[i].get()} {time_vals[i].get()}".strip()
        data[i]["read"] = done_vars[i].get()

    save_data(data)
    messagebox.showinfo("Saved", "Changes have been saved successfully!")
    load_data()

alerted = set()

def show_popup(task_text):
    win = Toplevel(root)
    win.title("Reminder")
    win.geometry("420x220+700+400")
    win.config(bg="#6C5CE7")

    inner = Frame(win, bg="#A29BFE", bd=6)
    inner.pack(expand=True, fill=BOTH, padx=8, pady=8)

    Label(inner, text="Reminder Alert", font=("Segoe UI", 20, "bold"),
          fg="white", bg="#6C5CE7").pack(pady=10)

    Label(inner, text=f"It's time for:\n\n{task_text}",
          font=("Segoe UI", 14, "bold"),
          fg="#FDFEFE", bg="#6C5CE7").pack(pady=10)

    Button(inner, text="Done", command=win.destroy,
           bg="#4834D4", fg="white",
           font=("Segoe UI", 12, "bold"), width=12).pack(pady=10)

    win.attributes("-topmost", True)
    win.after(10000, win.destroy)

def reminder_loop():
    while True:
        try:
            with open("tasks.json", "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        now = datetime.datetime.now().replace(second=0, microsecond=0)

        for t in data:
            key = f"{t['task']}_{t.get('datetime', '')}"
            try:
                when = datetime.datetime.strptime(t["datetime"], "%Y-%m-%d %H:%M")
            except Exception:
                continue

            if when == now and key not in alerted:
                root.after(0, lambda text=t["task"]: show_popup(text))
                alerted.add(key)

        time.sleep(60)

root = Tk()
root.title("To-Do List App with Reminders")
root.geometry("780x650")
root.configure(bg="#EBF5FB")

Label(root, text="To-Do List App with Reminders",
      font=("Segoe UI", 20, "bold"),
      bg="#5DADE2", fg="#FFD700", pady=10).pack(fill=X)

input_box = Frame(root, bg="#EBF5FB")
input_box.pack(pady=10)

Label(input_box, text="New Task:", font=("Segoe UI", 13, "bold"),
      bg="#EBF5FB").grid(row=0, column=0, padx=5)

new_task = StringVar()
Entry(input_box, textvariable=new_task,
      font=("Segoe UI", 12), width=45).grid(row=0, column=1, padx=5)

Label(input_box, text="Deadline:", font=("Segoe UI", 13, "bold"),
      bg="#EBF5FB").grid(row=1, column=0, pady=10)

cal = Calendar(
    input_box,
    selectmode="day",
    date_pattern="yyyy-mm-dd",
    background="#FFF0F5",
    foreground="#4A235A",
    headersbackground="#9966CC",
    headersforeground="white",
    weekendbackground="#DE6FA1",
    weekendforeground="white",
    selectbackground="#BB8FCE",
    selectforeground="white",
    normalbackground="#FFE4E1",
    normalforeground="#4A235A",
    othermonthforeground="#C39BD3",
    bordercolor="#9966CC",
    font=("Segoe UI", 10, "bold")
)
cal.grid(row=1, column=1, pady=5)

Label(input_box, text="Select Time:", font=("Segoe UI", 13, "bold"),
      bg="#EBF5FB").grid(row=2, column=0)

time_frame = Frame(input_box, bg="#EBF5FB")
time_frame.grid(row=2, column=1, pady=5)

hour_val, minute_val = StringVar(value="12"), StringVar(value="00")
hours = [f"{i:02d}" for i in range(24)]
minutes = [f"{i:02d}" for i in range(60)]

ttk.Combobox(time_frame, values=hours, width=5,
             textvariable=hour_val).grid(row=0, column=0, padx=5)

ttk.Combobox(time_frame, values=minutes, width=5,
             textvariable=minute_val).grid(row=0, column=1, padx=5)

btn_box = Frame(input_box, bg="#EBF5FB")
btn_box.grid(row=3, column=0, columnspan=2, pady=25)

Button(btn_box, text="Add Task", command=add_task,
       bg="#27AE60", fg="white",
       font=("Segoe UI", 12, "bold"),
       width=12).pack(side=LEFT, padx=10)

Button(btn_box, text="Save Edits", command=save_all,
       bg="#2980B9", fg="white",
       font=("Segoe UI", 12, "bold"),
       width=12).pack(side=LEFT, padx=10)

task_canvas = Canvas(root, bg="#EBF5FB", highlightthickness=0)
scroll_y = ttk.Scrollbar(root, orient="vertical",
                        command=task_canvas.yview)

task_frame = Frame(task_canvas, bg="#EBF5FB")
win_id = task_canvas.create_window((0, 0),
                                   window=task_frame,
                                   anchor="n")

def resize(event=None):
    w = task_canvas.winfo_width()
    task_canvas.itemconfig(win_id, width=w)
    task_canvas.coords(win_id, w / 2, 0)

task_canvas.bind("<Configure>", resize)
task_canvas.configure(yscrollcommand=scroll_y.set)

scroll_y.pack(side=RIGHT, fill=Y)
task_canvas.pack(fill=BOTH, expand=True, padx=10, pady=5)

task_container = Frame(task_frame, bg="#EBF5FB")
task_container.pack(anchor="center", pady=10)

load_data()

threading.Thread(target=reminder_loop, daemon=True).start()

root.mainloop()
