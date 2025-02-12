import tkinter as tk
from tkinter import messagebox, Menu, filedialog
import sqlite3
import yfinance as yf
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def update_time():
    """Update the current time on the label every second."""
    current_time = datetime.now().strftime("%B %d, %Y")
    label_time.config(text=current_time)


def get_stock_data():
    """Fetch stock data for the entered company code and period, then display it on a chart."""
    company_code = entry_company_code.get().strip()

    if not company_code:
        messagebox.showerror("Error", "Please enter a company code.")
        return

    try:
        period = period_slider.get()

        # Fetch stock data using yfinance
        stock = yf.Ticker(company_code)
        stock_info = stock.history(period=f"{period}d")

        if stock_info.empty:
            messagebox.showerror("Error", "No data available for the given company code.")
            return

        # Clear the previous chart if exists
        for widget in frame_chart.winfo_children():
            widget.destroy()

        # Plot the stock closing price on a graph
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(stock_info.index, stock_info['Close'])

        # Display the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=frame_chart)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Update the label with the current stock price
        current_price = stock_info['Close'].iloc[-1]
        label_stock_current_price.config(text=f"{current_price:.2f}")

    except ValueError:
        messagebox.showerror("Error", "Invalid company code")


def on_closing():
    """Handle the window close event."""
    window.quit()  # Ensure Tkinter's mainloop is stopped properly
    window.destroy()  # Close the window


def open_database():
    """Open a database file and display the first 10 records."""
    file_path = filedialog.askopenfilename(filetypes=[("SQLite Database", "*.db")])

    if not file_path:
        return

    # Connect to the SQLite database
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        # Fetch the first 10 records from the first table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            messagebox.showerror("Error", "No tables found in the database.")
            conn.close()
            return

        # Assume the first table is the one we want
        table_name = tables[0][0]
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
        rows = cursor.fetchall()

        # Display the records in the window
        for widget in frame_table.winfo_children():
            widget.destroy()

        if rows:
            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    label = tk.Label(frame_table, text=value, font=("Arial", 10), relief="solid", width=15)
                    label.grid(row=i, column=j, padx=5, pady=2)

        conn.close()

    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Database error: {e}")
        return


def close_table():
    """Close the table from the window."""
    for widget in frame_table.winfo_children():
        widget.destroy()


# Set up the main window
window = tk.Tk()
window.title("Stock Price Explorer")
window.geometry("800x600")

# Menu bar setup
menu_bar = Menu(window)
window.config(menu=menu_bar)

# File options
file_menu = Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=open_database)
file_menu.add_command(label="Close", command=close_table)

# Explore menu button (no cascade)
menu_bar.add_command(label="Explore", command=get_stock_data)

# Configure grid layout for the window
window.grid_columnconfigure(0, weight=1, minsize=100)
window.grid_columnconfigure(1, weight=0, minsize=100)

# Time label (current time)
label_time = tk.Label(window, font=("Arial", 14), anchor="w")
label_time.grid(row=0, column=0, padx=10, pady=0, sticky="w")

# Information label about the stock data source
label_info = tk.Label(
    window,
    text=(
        "The stock information provided is for informational purposes only and "
        "is not intended for trading purposes. The stock information and charts "
        "are provided by Yahoo Finance, a third-party service, and the owner does "
        "not provide information to this service."
    ),
    font=("Arial", 8),
    anchor="w",
    justify="left",
    wraplength=350,
)
label_info.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="w")

# Company code input label
label_company_code = tk.Label(window, text="Enter stock company code:", font=("Arial", 10))
label_company_code.grid(row=2, column=0, padx=10, pady=5, sticky="w")

# Company code input field
entry_company_code = tk.Entry(window, font=("Arial", 10))
entry_company_code.grid(row=3, column=0, padx=10, pady=5, sticky="w")

# Label to indicate pricing delay
label_delayed = tk.Label(window, text="Pricing delayed", font=("Arial", 14), anchor="e")
label_delayed.grid(row=0, column=1, padx=10, pady=10, sticky="ne")

# Label to show the current stock price
label_stock_current_price = tk.Label(window, text="", font=("Arial", 30), anchor="e")
label_stock_current_price.grid(row=1, column=1, padx=10, pady=0, sticky="ne")

# Frame for displaying the chart
frame_chart = tk.Frame(window)
frame_chart.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Frame for displaying the table
frame_table = tk.Frame(window)
frame_table.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

# Slider for selecting the time period
period_slider = tk.Scale(window, from_=1, to=365, orient="horizontal", label="Select Period:", font=("Arial", 10))
period_slider.set(30)
period_slider.grid(row=4, column=0, padx=10, pady=5, sticky="w")

# Update the current time every second
update_time()

# Handle the window close event
window.protocol("WM_DELETE_WINDOW", on_closing)

# Run the main loop for the Tkinter window
window.mainloop()
