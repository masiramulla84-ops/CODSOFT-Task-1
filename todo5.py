import customtkinter as ctk
import sqlite3
from datetime import datetime

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class TaskFlowPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TaskFlow Pro v2.0")
        self.geometry("600x900")
        self.configure(fg_color="#F0F2F5")

        self.init_db()
        self.setup_ui()
        self.refresh_tasks()

    def init_db(self):
        """Initializes database for tasks and subtasks."""
        self.conn = sqlite3.connect("taskflow_pro.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks 
            (id INTEGER PRIMARY KEY, title TEXT, priority TEXT, 
             category TEXT, due_date TEXT, status INTEGER)''')
        # Table for subtasks linked to a parent task
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS subtasks 
            (id INTEGER PRIMARY KEY, task_id INTEGER, title TEXT, status INTEGER)''')
        self.conn.commit()

    def setup_ui(self):
        """Creates a professional, clean layout."""
        # Header & Search
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=30, pady=20)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_tasks())
        self.search_bar = ctk.CTkEntry(self.top_frame, placeholder_text="🔍 Search tasks...",
                                       textvariable=self.search_var, height=45, corner_radius=10)
        self.search_bar.pack(side="left", fill="x", expand=True)

        # Progress Bar Section
        self.prog_card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=15)
        self.prog_card.pack(fill="x", padx=30, pady=10)
        self.prog_label = ctk.CTkLabel(self.prog_card, text="Productivity Score: 0%", font=("Arial", 12, "bold"))
        self.prog_label.pack(pady=(10, 0))
        self.bar = ctk.CTkProgressBar(self.prog_card, width=500, height=12, progress_color="#6C5CE7")
        self.bar.pack(pady=15)

        # Filters
        self.filter_menu = ctk.CTkSegmentedButton(self, values=["All", "Work", "Personal", "Completed"],
                                                  command=lambda v: self.refresh_tasks())
        self.filter_menu.set("All")
        self.filter_menu.pack(fill="x", padx=30, pady=10)

        # Task List
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20)

        # Floating Add Button
        self.add_btn = ctk.CTkButton(self, text="+ New Task", height=55, corner_radius=28,
                                     font=ctk.CTkFont(size=16, weight="bold"),
                                     fg_color="#6C5CE7", command=self.open_add_window)
        self.add_btn.pack(pady=20, padx=60, fill="x")

    def open_add_window(self):
        """Opens a professional popup to enter task details."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create New Task")
        dialog.geometry("400x500")
        dialog.attributes("-topmost", True)

        ctk.CTkLabel(dialog, text="Task Details", font=("Arial", 18, "bold")).pack(pady=20)

        entry = ctk.CTkEntry(dialog, placeholder_text="What needs to be done?", width=300)
        entry.pack(pady=10)

        prio_menu = ctk.CTkOptionMenu(dialog, values=["High", "Medium", "Low"], fg_color="#6C5CE7")
        prio_menu.pack(pady=10)

        cat_menu = ctk.CTkOptionMenu(dialog, values=["Work", "Personal"], fg_color="#6C5CE7")
        cat_menu.pack(pady=10)

        def save():
            if entry.get():
                date_str = datetime.now().strftime("%Y-%m-%d")
                self.cursor.execute("""INSERT INTO tasks (title, priority, category, due_date, status) 
                                       VALUES (?, ?, ?, ?, ?)""",
                                    (entry.get(), prio_menu.get(), cat_menu.get(), date_str, 0))
                self.conn.commit()
                self.refresh_tasks()
                dialog.destroy()

        ctk.CTkButton(dialog, text="Save Task", command=save, fg_color="#00B894").pack(pady=30)

    def refresh_tasks(self):
        """Reloads UI with filtering and search logic."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        search = self.search_var.get().lower()
        f_val = self.filter_menu.get()

        self.cursor.execute("SELECT * FROM tasks ORDER BY status ASC")
        rows = self.cursor.fetchall()

        for row in rows:
            tid, title, prio, cat, due, status = row
            # Filter Logic
            if search and search not in title.lower(): continue
            if f_val == "Completed" and status == 0: continue
            if f_val in ["Work", "Personal"] and cat != f_val: continue

            self.draw_task_card(row)

        self.update_progress(rows)

    def draw_task_card(self, row):
        """Draws a card with priority indicators and delete options."""
        tid, title, prio, cat, due, status = row
        p_color = {"High": "#FF7675", "Medium": "#FAB1A0", "Low": "#74B9FF"}.get(prio)

        card = ctk.CTkFrame(self.scroll_frame, fg_color="#FFFFFF", corner_radius=12, border_width=1,
                            border_color="#E0E0E0")
        card.pack(fill="x", pady=8, padx=5)

        cb = ctk.CTkCheckBox(card, text=title, font=ctk.CTkFont(size=14, weight="bold"),
                             command=lambda: self.toggle_task(tid, status))
        if status: cb.select()
        cb.pack(side="left", padx=15, pady=15)

        # Priority Tag
        tag = ctk.CTkLabel(card, text=prio, fg_color=p_color, text_color="white",
                           corner_radius=8, width=60, font=("Arial", 10, "bold"))
        tag.pack(side="right", padx=10)

        del_btn = ctk.CTkButton(card, text="🗑", width=30, fg_color="transparent",
                                text_color="gray", command=lambda: self.delete_task(tid))
        del_btn.pack(side="right")

    def toggle_task(self, tid, s):
        self.cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (1 if s == 0 else 0, tid))
        self.conn.commit()
        self.refresh_tasks()

    def delete_task(self, tid):
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (tid,))
        self.conn.commit()
        self.refresh_tasks()

    def update_progress(self, rows):
        total = len(rows)
        done = sum(1 for r in rows if r[5] == 1)
        if total > 0:
            val = done / total
            self.bar.set(val)
            self.prog_label.configure(text=f"Productivity Score: {int(val * 100)}%")


if __name__ == "__main__":
    app = TaskFlowPro()
    app.mainloop()