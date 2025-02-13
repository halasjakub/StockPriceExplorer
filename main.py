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

        # Clear the previous content (chart or table)
        clear_chart()

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

        # Adjust the frame size dynamically
        frame_chart.grid_rowconfigure(0, weight=1, minsize=300)  # Dynamic row size for chart
        frame_chart.grid_columnconfigure(0, weight=1, minsize=400)  # Dynamic column size for chart

    except ValueError:
        messagebox.showerror("Error", "Invalid company code")


def clear_chart():
    """Clear the content (chart or table) from the window."""
    for widget in frame_chart.winfo_children():
        widget.destroy()

    # Reset frame configuration after clearing
    frame_chart.grid_rowconfigure(0, weight=0, minsize=100)  # Reset row size
    frame_chart.grid_columnconfigure(0, weight=0, minsize=100)  # Reset column size


def export_data():
    """Export stock data to the SQLite database based on user input."""
    symbol = entry_company_code.get().strip()  # Get the value from entry_company_code
    adjustable_period = period_slider.get()  # Get the value from period_slider

    if not symbol:
        messagebox.showerror("Error", "Please enter a company code.")
        return

    # Fetch stock data using yfinance
    try:
        stock_data = yf.download(symbol, period=f"{adjustable_period}d", interval="1d")

        if stock_data.empty:
            messagebox.showerror("Error", "No data available for the given company code.")
            return

        # Connect to the SQLite database
        conn = sqlite3.connect('stocks.db')
        cursor = conn.cursor()

        # Create table if it doesn't exist, with a new 'symbol' column
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                symbol TEXT  -- New column to store the company symbol
            )
        ''')

        # Insert data into the database
        for index, row in stock_data.iterrows():
            date_str = index.strftime('%Y-%m-%d')  # Convert date to string
            open_price = round(float(row['Open']), 2)
            high_price = round(float(row['High']), 2)
            low_price = round(float(row['Low']), 2)
            close_price = round(float(row['Close']), 2)
            volume = int(row['Volume'])

            cursor.execute('''
                INSERT INTO stock_prices (date, open, high, low, close, volume, symbol)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (date_str, open_price, high_price, low_price, close_price, volume, symbol))

        conn.commit()
        conn.close()

        print("Data saved")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download stock data: {e}")


def clear_data():
    """Clear the content (chart or table) from the window and delete data from the database."""
    for widget in frame_chart.winfo_children():
        widget.destroy()

    frame_chart.grid_rowconfigure(0, weight=0, minsize=100)
    frame_chart.grid_columnconfigure(0, weight=0, minsize=100)

    try:
        conn = sqlite3.connect('stocks.db')
        cursor = conn.cursor()

        cursor.execute('DELETE FROM stock_prices')
        conn.commit()
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='stock_prices'")

        conn.commit()
        conn.close()

        print("Database cleared.")
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Database error: {e}")


def open_database():
    """Open a database file and display the first 10 records with a slicer for additional records."""
    file_path = filedialog.askopenfilename(filetypes=[("SQLite Database", "*.db")])

    if not file_path:
        return

    # Connect to the SQLite database
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            messagebox.showerror("Error", "No tables found in the database.")
            conn.close()
            return

        table_name = tables[0][0]
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Clear the previous content (chart or table)
        clear_chart()

        # Adding column headers
        column_names = ['ID', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Symbol']

        # Scrollable frame for table
        canvas = tk.Canvas(frame_chart)
        scrollbar = tk.Scrollbar(frame_chart, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollable_frame = tk.Frame(canvas)

        # Add the table content to the scrollable frame
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scrollbar.pack(side="left", fill="y")  # Scrollbar on the left
        canvas.pack(side="left", fill="both", expand=True)

        # Display column names as headers
        for col_num, col_name in enumerate(column_names):
            label = tk.Label(
                scrollable_frame, text=col_name, font=("Arial", 10, 'bold'), relief="solid", width=15
            )
            label.grid(row=0, column=col_num, padx=5, pady=2)

        # Display only the first 20 rows of data, rest should be scrollable
        for i, row in enumerate(rows[:20], start=1):  # Limit to 20 records
            for j, value in enumerate(row):
                label = tk.Label(
                    scrollable_frame, text=value, font=("Arial", 10), relief="solid", width=15
                )
                label.grid(row=i, column=j, padx=5, pady=2)

        frame_chart.grid_rowconfigure(0, weight=1, minsize=300)
        frame_chart.grid_columnconfigure(0, weight=1, minsize=400)

        conn.close()

    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Database error: {e}")
        return


def on_closing():
    """Handle the window close event."""
    window.quit()  # Ensure Tkinter's mainloop is stopped properly
    window.destroy()  # Close the window


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
file_menu.add_command(label="Close", command=clear_chart)

# Chart options
chart_menu = Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="Chart", menu=chart_menu)
chart_menu.add_command(label="Open", command=get_stock_data)
chart_menu.add_command(label="Close", command=clear_chart)

# Data options
data_menu = Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="Data", menu=data_menu)
data_menu.add_command(label="Export", command=export_data)
data_menu.add_command(label="Clear", command=clear_data)

# Explore menu button (no cascade)
menu_bar.add_command(label="Explore", command=get_stock_data)

# Configure grid layout for the window
window.grid_columnconfigure(0, weight=1, minsize=150)  # Left column for slicer
window.grid_columnconfigure(1, weight=3, minsize=100)  # Right column for table/chart
window.grid_rowconfigure(5, weight=1, minsize=300)  # Dynamic row for content

# Frame for displaying the slicer and stock information
frame_left = tk.Frame(window)
frame_left.grid(row=2, column=0, rowspan=3, padx=10, pady=10, sticky="nsew")

# Frame for displaying the chart or table
frame_chart = tk.Frame(window)
frame_chart.grid(row=5, column=1, padx=10, pady=10, sticky="nsew")

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

# Slider for selecting the time period
period_slider = tk.Scale(
    window, from_=1, to=365, orient="horizontal", label="Select Period:", font=("Arial", 10)
)
period_slider.set(30)
period_slider.grid(row=4, column=0, padx=10, pady=5, sticky="w")

# Update the current time every second
update_time()

# Handle the window close event
window.protocol("WM_DELETE_WINDOW", on_closing)

# Run the main loop for the Tkinter window
window.mainloop()
