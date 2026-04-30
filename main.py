import time
import random
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#test

# ==========================================
# SORTING ALGORITHMS
# ==========================================

def bubble_sort(arr):
    for i in range(len(arr)):
        swapped = False
        for j in range(len(arr) - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break


def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        left = arr[:mid]
        right = arr[mid:]

        merge_sort(left)
        merge_sort(right)

        i = j = k = 0
        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1

        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1

        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1


# ==========================================
# EXPERIMENT ENGINE
# ==========================================

class SortingExperiment:
    def __init__(self, sizes, trials=5):
        self.sizes = sizes
        self.trials = trials
        self.results = []

    def generate_data(self, size):
        return [random.randint(1, 100000) for _ in range(size)]

    def time_algorithm(self, func, data):
        start = time.perf_counter()
        func(data.copy())
        return time.perf_counter() - start

    def average_time(self, func, data):
        return sum(self.time_algorithm(func, data) for _ in range(self.trials)) / self.trials

    def run(self, progress_callback=None, log_callback=None):
        self.results.clear()
        total = len(self.sizes)

        for i, size in enumerate(self.sizes):
            data = self.generate_data(size)

            b = self.average_time(bubble_sort, data)
            ins = self.average_time(insertion_sort, data)
            m = self.average_time(merge_sort, data)
            bi = self.average_time(lambda x: sorted(x), data)

            self.results.append([size, b, ins, m, bi])

            if progress_callback:
                progress_callback((i + 1) / total * 100)

            if log_callback:
                log_callback(f"Size {size} completed")

        return self.results


# ==========================================
# GUI APPLICATION
# ==========================================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sorting Analyzer Pro")
        self.root.geometry("1150x700")

        self.dark_mode = True
        self.colors = {
            "dark_bg": "#040404",
            "dark_panel": "#2b2b2b",
            "light_bg": "#f5f5f5"
        }

        self.sizes = [10, 50, 100, 200, 300, 500, 750, 800, 1000, 1500, 2000, 3500, 5000, 7500]
        self.exp = SortingExperiment(self.sizes)

        self.setup_ui()
        self.apply_theme()

    # ---------------- UI ---------------- #

    def setup_ui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # Buttons
        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack()

        self.run_btn = tk.Button(frame, text="▶ Run Test", command=self.run_test, bg="#4CAF50", fg="white",font=("Segoe UI", 10))
        self.run_btn.grid(row=0, column=0, padx=10)
        tk.Button(frame, text="💾 Save CSV", command=self.save_csv).grid(row=0, column=1, padx=10)
        tk.Button(frame, text="📸 Save Graph", command=self.save_graph).grid(row=0, column=2, padx=10)


        # Progress
        self.progress = ttk.Progressbar(self.main_frame)
        self.progress.pack(fill="x", padx=10, pady=5)

        # Split layout
        content = tk.Frame(self.main_frame)
        content.pack(fill="both", expand=True)

        # Left: table
        left = tk.Frame(content)
        left.pack(side="left", fill="y", padx=10)

        self.tree = ttk.Treeview(left, columns=("Size", "Bubble", "Insertion", "Merge", "Built-in"), show="headings", height=15)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack()

        # Right: graph
        right = tk.Frame(content)
        right.pack(side="right", fill="both", expand=True)

        self.fig = plt.Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Status bar
        self.status = tk.Label(self.root, text="Ready", anchor="w")
        self.status.pack(fill="x", side="top")

    # ---------------- LOGIC ---------------- #

    def run_test(self):
        self.status.config(text="Running experiment...")
        self.tree.delete(*self.tree.get_children())

        def progress(val):
            self.progress["value"] = val
            self.root.update_idletasks()

        results = self.exp.run(progress_callback=progress)

        for row in results:
            self.tree.insert("", tk.END, values=[f"{v:.5f}" if isinstance(v, float) else v for v in row])

        self.plot(results)
        self.status.config(text="Completed")

    def plot(self, results):
        self.ax.clear()

        sizes = [r[0] for r in results]
        self.ax.plot(sizes, [r[1] for r in results], marker='o', label="Bubble")
        self.ax.plot(sizes, [r[2] for r in results], marker='o', label="Insertion")
        self.ax.plot(sizes, [r[3] for r in results], marker='o', label="Merge")
        self.ax.plot(sizes, [r[4] for r in results], marker='o', label="Built-in")

        self.ax.set_title("Sorting Performance")
        self.ax.set_xlabel("Input Size")
        self.ax.set_ylabel("Time (s)")
        self.ax.legend()
        self.ax.grid()

        self.canvas.draw()

    def save_csv(self):
        with open("sorting_results.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Size", "Bubble", "Insertion", "Merge", "Built-in"])
            writer.writerows(self.exp.results)
        messagebox.showinfo("Saved", "CSV saved!")

    def save_graph(self):
        file = filedialog.asksaveasfilename(defaultextension=".png")
        if file:
            self.fig.savefig(file)
            messagebox.showinfo("Saved", "Graph saved!")

    # ---------------- THEME ---------------- #
    def apply_theme(self):
        bg = "#121212" if self.dark_mode else "#f5f5f5"
        panel = "#1e1e1e" if self.dark_mode else "#ffffff"
        fg = "white" if self.dark_mode else "black"

        # Root + main
        self.root.configure(bg=bg)
        self.main_frame.configure(bg=bg)

        # Frames
        for widget in self.root.winfo_children():
            try:
                widget.configure(bg=bg)
            except:
                pass

        # Table style (Treeview)
        style = ttk.Style()
        style.theme_use("default")

        if self.dark_mode:
            style.configure("Treeview",
                            background=panel,
                            foreground="white",
                            fieldbackground=panel)
            style.configure("Treeview.Heading",
                            background="#333333",
                            foreground="white")
        else:
            style.configure("Treeview",
                            background="white",
                            foreground="black",
                            fieldbackground="white")

        # Status bar
        self.status.configure(bg=panel, fg=fg)

        # Graph styling
        self.ax.set_facecolor(panel)
        self.fig.patch.set_facecolor(bg)

        for spine in self.ax.spines.values():
            spine.set_color(fg)

        self.ax.tick_params(colors=fg)
        self.ax.title.set_color(fg)
        self.ax.xaxis.label.set_color(fg)
        self.ax.yaxis.label.set_color(fg)

        self.canvas.draw()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()


    # ---------------- END ---------------- #


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()