import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import tkinter.ttk as ttk
import csv
import numpy as np
import statistics
import matplotlib.pyplot as plt


class App:
    def __init__(self, master):
        self.master = master
        self.master.title("CSV Viewer")

        self.master.geometry("800x600")  # Ustawienie domyślnego rozmiaru okna
        self.master.maxsize(width=self.master.winfo_screenwidth(), height=self.master.winfo_screenheight())

        style = ttk.Style()
        style.theme_use('clam')

        # self.load_button = ttk.Menubutton(self.master, text="Load CSV", direction='below')

        self.load_button = ttk.Menubutton(self.master, text="File")
        self.load_button.menu = tk.Menu(self.load_button, tearoff=0)
        self.load_button["menu"] = self.load_button.menu
        self.load_button.menu.add_command(label="Open", command=self.load_csv)
        self.load_button.menu.add_command(label="Export", command=self.export_data)
        self.load_button.menu.add_command(label="Create Plot", command=self.create_plot)

        self.load_button.pack(anchor=tk.W, fill=tk.X, expand=True)

        style = ttk.Style()
        style.configure('Custom.TMenubutton', padding=3)
        self.load_button.configure(style='Custom.TMenubutton')

        self.load_button.pack()

        self.load_button.pack()

        self.tree_frame = tk.Frame(self.master)
        self.tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


        self.tree_scrollbar_x = tk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)
        self.tree_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree_scrollbar_y = tk.Scrollbar(self.tree_frame)
        self.tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.treeview = tk.ttk.Treeview(self.tree_frame, columns=[], show='headings', xscrollcommand=self.tree_scrollbar_x.set, yscrollcommand=self.tree_scrollbar_y.set)
        self.treeview.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.tree_scrollbar_x.config(command=self.treeview.xview)
        self.tree_scrollbar_y.config(command=self.treeview.yview)

        # Add new tab for min/max values
        self.tabControl = ttk.Notebook(self.master)
        self.tabControl.pack(expand=1, fill="both")

        self.min_max_tab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.min_max_tab, text="Specific Values")

        # Add Treeview widget for min/max values
        self.min_max_treeview = ttk.Treeview(self.min_max_tab,
                                             columns=["Column", "Min", "Max", "Mean", "Median", "Mode", "St_dev"],
                                             show="headings")

        self.min_max_treeview.column("Column", minwidth=100, width=200)
        self.min_max_treeview.column("Min", minwidth=75, width=75)
        self.min_max_treeview.column("Max", minwidth=75, width=75)
        self.min_max_treeview.column("Mean", minwidth=75, width=75)
        self.min_max_treeview.column("Median", minwidth=75, width=75)
        self.min_max_treeview.column("Mode", minwidth=75, width=75)
        self.min_max_treeview.column("St_dev", minwidth=75, width=75)

        self.min_max_treeview.heading("Column", text="Column")
        self.min_max_treeview.heading("Min", text="Min")
        self.min_max_treeview.heading("Max", text="Max")
        self.min_max_treeview.heading("Mean", text="Mean")
        self.min_max_treeview.heading("Median", text="Median")
        self.min_max_treeview.heading("Mode", text="Mode")
        self.min_max_treeview.heading("St_dev", text="St_dev")

        self.min_max_treeview.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.min_max_button = ttk.Button(self.min_max_tab, text="Calculate", command=self.calculate_min_max)
        self.min_max_button.pack(side=tk.BOTTOM)

        # Add new tab for correlation matrix
        self.correlation_tab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.correlation_tab, text="Correlations")

        # Add Treeview widget for correlation matrix
        self.correlation_treeview = ttk.Treeview(self.correlation_tab, columns=[], show="headings")
        self.correlation_treeview.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.correlation_button = ttk.Button(self.correlation_tab, text="Calculate",
                                             command=self.calculate_correlation)
        self.correlation_button.pack(side=tk.BOTTOM)

    def load_csv(self):
        # Usuń stare dane
        self.treeview.delete(*self.treeview.get_children())

        file_path = filedialog.askopenfilename(title="Open CSV File",
                                               filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")))
        if file_path:
            with open(file_path, "r") as f:
                reader = csv.reader(f)
                data = []
                for row in reader:
                    data.append(row)
            self.display_table(data)

    def display_table(self, data):
        columns = data[0]
        self.treeview["columns"] = columns
        for col in columns:
            self.treeview.column(col, width=100, anchor=tk.CENTER)
            self.treeview.heading(col, text=col, anchor=tk.CENTER)
        for row in data[1:]:
            self.treeview.insert("", tk.END, values=row)

    def calculate_min_max(self):
        # Clear existing data from Treeview
        self.min_max_treeview.delete(*self.min_max_treeview.get_children())

        # Get data from Treeview
        data = []
        for idx, column in enumerate(self.treeview["columns"]):
            data.append([column])
            for item in self.treeview.get_children():
                value = self.treeview.set(item, column)
                data[idx].append(value)

        # Calculate statistics for each column
        statistics_values = []
        for col_idx in range(len(data)):
            column_data = [float(value) for value in data[col_idx][1:]]
            min_value = min(column_data)
            max_value = max(column_data)
            column_name = data[col_idx][0]
            mean_value = round(statistics.mean(column_data),2)
            median_value = statistics.median(column_data)
            mode_value = statistics.mode(column_data)
            stdev_value = round(statistics.stdev(column_data),2)
            statistics_values.append(
                (column_name, min_value, max_value, mean_value, median_value, mode_value, stdev_value))

        # Insert statistics values into Treeview
        for i, (column_name, min_value, max_value, mean_value,median_value, mode_value, stdev_value) in enumerate(
                statistics_values):
            self.min_max_treeview.insert("", tk.END, values=[column_name, min_value, max_value, mean_value,
                                                             median_value, mode_value, stdev_value])

            for col in self.min_max_treeview["columns"]:
                self.min_max_treeview.column(col, anchor="center")

    def calculate_correlation(self):
        # Clear existing data from Treeview
        self.correlation_treeview.delete(*self.correlation_treeview.get_children())

        # Get data from Treeview
        data = []
        columns = []
        for idx, column in enumerate(self.treeview["columns"]):
            is_number = True
            column_data = []
            for item in self.treeview.get_children():
                value = self.treeview.set(item, column)
                try:
                    column_data.append(float(value))
                except ValueError:
                    is_number = False
                    break
            if is_number:
                data.append(column_data)
                columns.append(column)

        # Calculate correlation matrix
        data = np.array(data, dtype=np.float64)
        correlation_matrix = np.corrcoef(data)

        # Insert correlation matrix into Treeview
        self.correlation_treeview["columns"] = columns
        for col in columns:
            self.correlation_treeview.column(col, width=100, anchor=tk.CENTER)
            self.correlation_treeview.heading(col, text=col, anchor=tk.CENTER)
        for i, row in enumerate(correlation_matrix):
            values = [round(x, 2) for x in row]
            self.correlation_treeview.heading(columns[0], text=" ", anchor=tk.CENTER)
            self.correlation_treeview.insert("", tk.END, values=[columns[i]] + values)

    def export_data(self):
        selected_rows = self.treeview.selection()
        if not selected_rows:
            return
        file_path = filedialog.asksaveasfilename(title="Save CSV File", defaultextension=".csv",
                                                 filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")))
        if file_path:
            selected_data = []
            # Pobierz nagłówki z głównego pliku
            headers = [self.treeview.heading(col)["text"] for col in self.treeview["columns"]]
            selected_data.append(headers)  # Dodaj nagłówki do wybranych danych
            for row in selected_rows:
                values = [self.treeview.set(row, col) for col in self.treeview["columns"]]
                selected_data.append(values)
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(selected_data)

    def create_plot(self):
        selected_items = self.treeview.get_children()
        values_4 = []
        values_7 = []
        for item in selected_items:
            values_4.append(float(self.treeview.item(item, "values")[3]))
            values_7.append(float(self.treevgiew.item(item, "values")[6]))

        plt.figure(figsize=(8, 6))
        plt.bar(values_4, values_7)
        plt.xlabel("Number of Childs")
        plt.ylabel("Life Standards")
        plt.title("Statistic 1")
        plt.show()

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()