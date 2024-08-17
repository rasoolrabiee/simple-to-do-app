import tkinter as tk
from tkinter import simpledialog
import json
import os

class TodoListApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("To-Do List")
        self.geometry('400x300')
        self.attributes('-alpha', 0.9)

        self.drag_start_y = 0
        self.dragging_widgets = None

        # Colors
        self.bg_color = "#F9D5B6"
        self.header_bg_color = "#F8B195"
        self.label_bg_color = "#F8E4D9"
        self.checked_row_color = "#32CD32"

        # Font size
        self.font_size = 10

        # main frame
        self.main_frame = tk.Frame(self, bg=self.bg_color, width=400, height=300)
        self.main_frame.pack_propagate(False)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame for buttons
        self.button_frame = tk.Frame(self.main_frame, bg=self.bg_color, height=30)
        self.button_frame.pack(pady=0, fill=tk.X)

        self.add_button = tk.Button(self.button_frame, text="+", command=self.add_row, bg=self.header_bg_color, font=('Helvetica', self.font_size, 'bold'), width=2)
        self.add_button.pack(pady=5, side="left")
        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_tasks, bg=self.header_bg_color, font=('Helvetica', self.font_size, 'bold'))
        self.save_button.pack(pady=5, side="left")
        self.load_button = tk.Button(self.button_frame, text="Load", command=self.load_tasks, bg=self.header_bg_color, font=('Helvetica', self.font_size, 'bold'))
        self.load_button.pack(pady=5, side="left")

        # Canvas for scrolling
        self.canvas = tk.Canvas(self.main_frame, bg=self.bg_color)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.task_frame = tk.Frame(self.canvas, bg=self.bg_color)
        self.canvas.create_window((0, 0), window=self.task_frame, anchor="nw")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)
        self.task_frame.bind("<Configure>", self.update_scrollregion)

        self.entries = []
        self.check_vars = {}


    def add_row(self):
        task = simpledialog.askstring("Input", "Enter the task:")
        if task is None: return
        intro = simpledialog.askstring("Input", "Enter the introduction:")
        if intro is None: return
        time = simpledialog.askstring("Input", "Enter the time:")
        if time is None: return

        row_number = len(self.entries) + 1
        check_var = tk.BooleanVar()
        check_button = tk.Checkbutton(self.task_frame, variable=check_var, bg=self.bg_color, command=lambda: self.update_row_color(check_var, row_number))
        task_label = tk.Label(self.task_frame, text=task, bg=self.label_bg_color, borderwidth=1, relief=tk.SOLID, padx=10, pady=5, font=('Helvetica', self.font_size), wraplength=50)
        intro_label = tk.Label(self.task_frame, text=intro, bg=self.label_bg_color, borderwidth=1, relief=tk.SOLID, padx=10, pady=5, font=('Helvetica', self.font_size), wraplength=200, width=5)
        time_label = tk.Label(self.task_frame, text=time, bg=self.label_bg_color, borderwidth=1, relief=tk.SOLID, padx=10, pady=5, font=('Helvetica', self.font_size), wraplength=200, width=5)
        delete_button = tk.Button(self.task_frame, text="-", command=lambda: self.delete_row(check_button), bg="#FF6F61", font=('Helvetica', self.font_size, 'bold'), width=2)

        # for drag the whole row
        task_label.bind("<ButtonPress-1>", lambda e, task_label=task_label, intro_label=intro_label, time_label=time_label: self.on_drag_start(e, task_label, intro_label, time_label))
        task_label.bind("<B1-Motion>", self.on_drag_motion)
        task_label.bind("<ButtonRelease-1>", self.on_drag_stop)

        check_button.grid(row=row_number, column=0, padx=5, pady=5, sticky="nsew")
        task_label.grid(row=row_number, column=1, padx=5, pady=5, sticky="nsew")
        intro_label.grid(row=row_number, column=2, padx=5, pady=5, sticky="nsew")
        time_label.grid(row=row_number, column=3, padx=5, pady=5, sticky="nsew")
        delete_button.grid(row=row_number, column=4, padx=5, pady=5)

        self.entries.append((check_button, task_label, intro_label, time_label, delete_button))
        self.check_vars[check_button] = check_var

        for col in range(5):
            self.task_frame.grid_columnconfigure(col, weight=1)
        self.task_frame.grid_rowconfigure(row_number, weight=1)
        self.update_scrollregion()

    def update_row_color(self, check_var, row_number):
        is_checked = check_var.get()
        row_widgets = self.entries[row_number - 1]
        color = self.checked_row_color if is_checked else self.label_bg_color
        for widget in row_widgets:
            if isinstance(widget, (tk.Label, tk.Checkbutton)):
                widget.config(bg=color)

    def delete_row(self, check_button):
        for entry in self.entries:
            if entry[0] == check_button:
                for widget in entry:
                    widget.grid_forget()  # Remove the widget from the grid
                self.entries.remove(entry)  # Remove the entry from the list
                del self.check_vars[check_button]  # Remove the entry from the check_vars
                break

        # Re-grid the remaining entris
        for i, entry in enumerate(self.entries):
            for widget in entry:
                widget.grid(row=i + 1, column=widget.grid_info()['column'], padx=5, pady=5, sticky="nsew")

        self.update_scrollregion()


    def save_tasks(self):
        tasks_data = []
        for entry in self.entries:
            check_button, task_label, intro_label, time_label, _ = entry
            task = task_label.cget("text")
            intro = intro_label.cget("text")
            time = time_label.cget("text")
            check_var = self.check_vars.get(check_button)
            checked = check_var.get() if check_var else False
            tasks_data.append({"task": task, "intro": intro, "time": time, "checked": checked})
        try:
            with open("tasks.json", "w") as f:
                json.dump(tasks_data, f)
        except IOError as e:
            print(f"Error saving tasks: {e}")

    def load_tasks(self):
        if not os.path.exists("tasks.json"):
            return
        try:
            with open("tasks.json", "r") as f:
                tasks_data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading tasks: {e}")
            return
        for entry in self.entries:
            for widget in entry:
                widget.grid_forget()
        self.entries = []
        self.check_vars = {}
        for i, task_data in enumerate(tasks_data):
            check_var = tk.BooleanVar(value=task_data["checked"])
            row_number = i + 1
            check_button = tk.Checkbutton(self.task_frame, variable=check_var, bg=self.bg_color, command=lambda v=check_var, r=row_number: self.update_row_color(v, r))
            task_label = tk.Label(self.task_frame, text=task_data["task"], bg=self.label_bg_color, borderwidth=1, relief=tk.SOLID, padx=10, pady=5, font=('Helvetica', self.font_size), wraplength=50)
            intro_label = tk.Label(self.task_frame, text=task_data["intro"], bg=self.label_bg_color, borderwidth=1, relief=tk.SOLID, padx=10, pady=5, font=('Helvetica', self.font_size), wraplength=200, width=5)
            time_label = tk.Label(self.task_frame, text=task_data["time"], bg=self.label_bg_color, borderwidth=1, relief=tk.SOLID, padx=10, pady=5, font=('Helvetica', self.font_size), wraplength=200, width=5)
            delete_button = tk.Button(self.task_frame, text="-", command=lambda b=check_button: self.delete_row(b), bg="#FF6F61", font=('Helvetica', self.font_size, 'bold'), width=2)


            task_label.bind("<ButtonPress-1>", lambda e, task_label=task_label, intro_label=intro_label, time_label=time_label: self.on_drag_start(e, task_label, intro_label, time_label))
            task_label.bind("<B1-Motion>", self.on_drag_motion)
            task_label.bind("<ButtonRelease-1>", self.on_drag_stop)

            check_button.grid(row=row_number, column=0, padx=5, pady=5, sticky="nsew")
            task_label.grid(row=row_number, column=1, padx=5, pady=5, sticky="nsew")
            intro_label.grid(row=row_number, column=2, padx=5, pady=5, sticky="nsew")
            time_label.grid(row=row_number, column=3, padx=5, pady=5, sticky="nsew")
            delete_button.grid(row=row_number, column=4, padx=5, pady=5)

            self.entries.append((check_button, task_label, intro_label, time_label, delete_button))
            self.check_vars[check_button] = check_var
        self.update_scrollregion()

    def update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_drag_start(self, event, task_label, intro_label, time_label):
        self.drag_start_y = event.y
        self.dragging_widgets = [task_label, intro_label, time_label]
        for widget in self.dragging_widgets:
            widget.lift()

    # def on_drag_motion(self, event):
    #     y = event.y_root - self.winfo_rooty()
    #     for widget in self.dragging_widgets:
    #         widget.place_configure(y=y + widget.winfo_y() - self.drag_start_y)
    #     self.update_order()

    def on_drag_stop(self, event):
        self.dragging_widgets = None
        for entry in self.entries:
            for widget in entry:
                widget.grid_configure()
        self.update_order()

    def on_drag_motion(self, event):
        if self.dragging_widgets:
            # Calculate  new position for drag
            delta_y = event.y - self.drag_start_y
            new_y = self.dragging_widgets[0].winfo_y() + delta_y
            
            # Move all dragging widgets to the new position
            for widget in self.dragging_widgets:
                widget.place_configure(y=new_y)
            
            # Update the start position for further dragging
            self.drag_start_y = event.y
            self.update_order()

    def update_order(self):
        positions = []
        for entry in self.entries:
            task_label = entry[1]
            y_position = task_label.winfo_y()
            positions.append((y_position, entry))
        
        # Sort entries based on their vertical positions
        sorted_entries = [entry for _, entry in sorted(positions, key=lambda x: x[0])]
        
        self.entries = sorted_entries

        # Regrid the widgets
        for i, entry in enumerate(self.entries):
            for widget in entry:
                grid_info = widget.grid_info()
                if 'column' in grid_info: 
                    widget.grid(row=i + 1, column=grid_info['column'], padx=5, pady=5, sticky="nsew")
        
        self.update_scrollregion()




if __name__ == "__main__":
    app = TodoListApp()
    app.mainloop()
