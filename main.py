import tkinter as tk
from collections import Counter
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
        self.master.title("STATISTIC REVIEW 1.0")

        self.master.geometry("1200x600")  # Ustawienie domyślnego rozmiaru okna
        self.master.maxsize(width=self.master.winfo_screenwidth(), height=self.master.winfo_screenheight())

        style = ttk.Style()
        style.theme_use('clam')

        # self.load_button = ttk.Menubutton(self.master, text="Load CSV", direction='below')

        self.load_button = ttk.Menubutton(self.master, text="File")
        self.load_button.menu = tk.Menu(self.load_button, tearoff=0)
        self.load_button["menu"] = self.load_button.menu
        self.load_button.menu.add_command(label="Open Data", command=self.load_csv)
        self.load_button.menu.add_command(label="Export Data", command=self.export_data)
        self.load_button.menu.add_command(label="Create Plot", command=self.create_plot)
        self.load_button.menu.add_command(label="Classify Data", command=self.open_classify_dialog)

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
                                             columns=["Column", "Min", "Max", "Mean", "Median", "Mode", "St_dev", "text_value_counts"],
                                             show="headings")

        self.min_max_treeview.column("Column", minwidth=100, width=200)
        self.min_max_treeview.column("Min", minwidth=75, width=75)
        self.min_max_treeview.column("Max", minwidth=75, width=75)
        self.min_max_treeview.column("Mean", minwidth=75, width=75)
        self.min_max_treeview.column("Median", minwidth=75, width=75)
        self.min_max_treeview.column("Mode", minwidth=75, width=75)
        self.min_max_treeview.column("St_dev", minwidth=75, width=75)
        self.min_max_treeview.column("text_value_counts", minwidth=200, width=200)

        self.min_max_treeview.heading("Column", text="Column")
        self.min_max_treeview.heading("Min", text="Min")
        self.min_max_treeview.heading("Max", text="Max")
        self.min_max_treeview.heading("Mean", text="Mean")
        self.min_max_treeview.heading("Median", text="Median")
        self.min_max_treeview.heading("Mode", text="Mode")
        self.min_max_treeview.heading("St_dev", text="St_dev")
        self.min_max_treeview.heading("text_value_counts", text="Qnt Of Text Value")

        self.min_max_treeview.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.min_max_button = ttk.Button(self.min_max_tab, text="Calculate", command=self.calculate_detailed)
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

    def calculate_detailed(self):
        # Check if the window is already open
        if getattr(self, "min_max_window", None) is not None and self.min_max_window.winfo_exists():
            # Window is already open, do nothing
            return

        # Create a new window
        self.min_max_window = tk.Toplevel(self.master)
        min_max_window = self.min_max_window
        min_max_window.title("Select Columns")

        # Configure the window size and position
        window_width = 400
        window_height = 300
        screen_width = min_max_window.winfo_screenwidth()
        screen_height = min_max_window.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        min_max_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Create a label
        label = ttk.Label(min_max_window, text="Select columns for statistical calculations",
                          font=("Arial", 14, "bold"))
        label.pack(pady=20)

        # Create a listbox to display available columns
        listbox = tk.Listbox(min_max_window, selectmode=tk.MULTIPLE, font=("Arial", 12), height=8)
        listbox.pack()

        # Add columns to the listbox
        columns = self.treeview["columns"]
        for column in columns:
            listbox.insert(tk.END, column)

        # Select all columns by default
        listbox.selection_set(0, tk.END)

        def calculate():
            # Get selected columns
            selected_columns = [listbox.get(index) for index in listbox.curselection()]

            if len(selected_columns) == 0:
                # Show error message if no columns are selected
                messagebox.showerror("Error", "Please select at least one column.")
                return

            # Clear existing data from Treeview
            self.min_max_treeview.delete(*self.min_max_treeview.get_children())

            # Get data from Treeview
            data = []
            for idx, column in enumerate(self.treeview["columns"]):
                if column in selected_columns:
                    column_data = []
                    for item in self.treeview.get_children():
                        value = self.treeview.set(item, column)
                        try:
                            column_data.append(float(value))
                        except ValueError:
                            column_data.append(value)  # Handle text values
                    data.append(column_data)

            # Calculate statistics for each selected column
            statistics_values = []
            for col_idx in range(len(data)):
                column_data = data[col_idx]
                column_name = selected_columns[col_idx]
                if all(isinstance(val, float) for val in column_data):
                    # Numeric column
                    min_value = min(column_data)
                    max_value = max(column_data)
                    mean_value = round(statistics.mean(column_data), 2)
                    stdev_value = round(statistics.stdev(column_data), 2)
                    median_value = statistics.median(column_data)
                    mode_value = statistics.mode(column_data)
                    value_counts = ""
                else:
                    # Text column
                    counter = Counter(column_data)
                    mode_value = counter.most_common(1)[0][0] if counter else ""
                    min_value = ""
                    max_value = ""
                    mean_value = ""
                    stdev_value = ""
                    median_value = ""
                    value_counts = ", ".join(f"{value}: {count}" for value, count in counter.items())

                statistics_values.append(
                    (
                    column_name, min_value, max_value, mean_value, median_value, mode_value, stdev_value, value_counts))

            # Insert statistics values into Treeview
            for i, (column_name, min_value, max_value, mean_value, median_value, mode_value, stdev_value,
                    value_counts) in enumerate(
                    statistics_values):
                self.min_max_treeview.insert("", tk.END,
                                             values=[column_name, min_value, max_value, mean_value,
                                                     median_value, mode_value, stdev_value, value_counts])

            for col in self.min_max_treeview["columns"]:
                self.min_max_treeview.column(col, anchor="center")

            # Close the window
            min_max_window.destroy()

        # Create a button to calculate statistics
        calculate_button = ttk.Button(min_max_window, text="Calculate", command=calculate)
        calculate_button.pack()

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
        self.correlation_treeview["columns"] = [" "] + columns
        self.correlation_treeview.column("#0", width=100, anchor=tk.CENTER)
        self.correlation_treeview.heading("#0", text=" ", anchor=tk.CENTER)
        for col in columns:
            self.correlation_treeview.column(col, width=100, anchor=tk.CENTER)
            self.correlation_treeview.heading(col, text=col, anchor=tk.CENTER)
        for i, row in enumerate(correlation_matrix):
            values = [round(x, 2) for x in row]
            self.correlation_treeview.insert("", tk.END, values=[columns[i]] + values)

    def export_data(self):
        selected_rows = self.treeview.selection()
        if not selected_rows:
            messagebox.showinfo("No Selection", "No rows selected.")
            return

        # Create dialog window
        dialog_window = tk.Toplevel(self.master)
        dialog_window.title("Select Columns")

        # Create listbox to select columns
        listbox = tk.Listbox(dialog_window, selectmode=tk.MULTIPLE)
        listbox.pack(padx=10, pady=10)

        # Add columns to listbox
        columns = self.treeview["columns"]
        for column in columns:
            listbox.insert(tk.END, column)

        def export_selected_columns():
            # Get selected columns from listbox
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showinfo("No Selection", "No columns selected.")
                dialog_window.destroy()
                return

            selected_columns = [columns[idx] for idx in selected_indices]

            file_path = filedialog.asksaveasfilename(
                title="Save CSV File", defaultextension=".csv",
                filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")))

            if file_path:
                selected_data = []
                headers = [self.treeview.heading(col)["text"] for col in selected_columns]
                selected_data.append(headers)  # Add headers to selected data

                for row in selected_rows:
                    values = [self.treeview.set(row, col) for col in selected_columns]
                    selected_data.append(values)

                with open(file_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(selected_data)

            # Close dialog window
            dialog_window.destroy()

        # Add button to export selected columns
        export_button = tk.Button(dialog_window, text="Export", command=export_selected_columns)
        export_button.pack(padx=10, pady=10)

        # Run the dialog window
        self.master.wait_window(dialog_window)

    def create_plot(self):
        # Check if any items are selected in Treeview
        selected_items = self.treeview.selection()

        if not selected_items:
            messagebox.showinfo("No Selection", "No rows selected.")
            return
        # Create dialog window
        dialog_window = tk.Toplevel(self.master)
        dialog_window.title("Select Columns and Chart Type")

        # Create listbox to select columns
        listbox = tk.Listbox(dialog_window, selectmode=tk.MULTIPLE)
        listbox.pack(padx=10, pady=5)

        # Add columns to listbox
        columns = self.treeview["columns"]
        for column in columns:
            listbox.insert(tk.END, column)

        # Create radio buttons for chart type
        chart_type_var = tk.StringVar()
        chart_type_var.set("line")
        chart_type_frame = tk.Frame(dialog_window)
        chart_type_frame.pack(padx=10, pady=5)

        tk.Label(chart_type_frame, text="Chart Type:").pack(side=tk.LEFT)

        chart_types = [("Scatter", "scatter"), ("Bar", "bar")]
        for chart_label, chart_type in chart_types:
            tk.Radiobutton(
                chart_type_frame,
                text=chart_label,
                variable=chart_type_var,
                value=chart_type
            ).pack(side=tk.LEFT)

        def plot_selected_columns():
            # Get selected columns from listbox
            chart_type = chart_type_var.get()

            selected_indices = listbox.curselection()
            if chart_type == "bar":
                if len(selected_indices) != 1:
                    messagebox.showinfo("Invalid Selection", "Please select one column for this type of chart.")
                    return
            else:
                if len(selected_indices) != 2:
                    messagebox.showinfo("Invalid Selection", "Please select exactly two columns.")
                    return

            selected_columns = [columns[idx] for idx in selected_indices]

            # Get column values
            x_values = []
            y_values = []
            for item in selected_items:
                item_values = self.treeview.item(item, "values")
                x_values.append(float(item_values[selected_indices[0]]))  # Use the first selected column for x-axis

                if len(selected_indices) > 1:
                    y_values.append(
                        float(item_values[selected_indices[1]]))  # Use the second selected column for y-axis

            # Get selected chart type
            # Create plot
            plt.figure(figsize=(8, 6))

            if chart_type == "scatter":
                plt.scatter(x_values, y_values, color='b', marker='o')  # Plot as scatter points
            elif chart_type == "bar":
                if len(selected_indices) == 1:
                    unique_x_values = list(set(x_values))
                    y_counts = [x_values.count(value) for value in unique_x_values]
                    plt.bar(unique_x_values, y_counts, color='b')  # Plot as bar chart with counts on y-axis
                    plt.xlabel(selected_columns[0])  # Label x-axis with the selected column
                    plt.ylabel("Count")  # Label y-axis as "Count"
                else:
                    plt.bar(x_values, y_values, color='b')  # Plot as bar chart
                    plt.xlabel(selected_columns[0])  # Label x-axis with the first selected column
                    plt.ylabel(selected_columns[1])  # Label y-axis with the second selected column

            plt.title("Plot Title")
            plt.show()

            # Close dialog window
            dialog_window.destroy()

        # Add button to plot selected columns
        plot_button = tk.Button(dialog_window, text="Plot", command=plot_selected_columns)
        plot_button.pack(padx=10, pady=5)

        # Run the dialog window
        self.master.wait_window(dialog_window)

    def open_classify_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Klasyfikacja")

        column_label = ttk.Label(dialog, text="Wybierz kolumnę:")
        column_label.pack()

        column_combobox = ttk.Combobox(dialog, values=self.get_column_names())
        column_combobox.pack()

        row_label = ttk.Label(dialog, text="Wybierz wiersz:")
        row_label.pack()

        row_combobox = ttk.Combobox(dialog, values=self.get_row_names())
        row_combobox.pack()

        classify_button = ttk.Button(dialog, text="Klasyfikuj",
                                     command=lambda: self.classify_data(dialog, column_combobox.get(),
                                                                        row_combobox.get()))
        classify_button.pack()

    def classify_data(self, dialog, selected_column, selected_row):
        selected_item = self.treeview.selection()

        if selected_column and selected_row:
            threshold = 0.5  # Próg klasyfikacji

            # Pobierz wybrany element danych
            item = self.treeview.set(selected_item, selected_column)
            if item:
                # Klasyfikacja danych na podstawie progu
                if float(item.values()) > threshold:
                    classification = "Pozytywny"
                else:
                    classification = "Negatywny"

                # Wyświetl wynik klasyfikacji
                messagebox.showinfo("Klasyfikacja", f"Wynik klasyfikacji: {classification}")
            else:
                messagebox.showwarning("Błąd", "Brak wartości dla wybranego elementu.")
        else:
            messagebox.showwarning("Błąd", "Nie wybrano żadnego elementu, kolumny lub wiersza.")

    def get_column_names(self):
        # Zwróć nazwy kolumn jako listę
        if self.treeview['columns']:
            return self.treeview['columns']
        else:
            return []

    def get_row_names(self):
        # Zwróć nazwy wierszy jako listę
        rows = self.treeview.get_children()
        return rows


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
