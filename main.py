# pip install yfinance
# pip install tkcalendar

# pip install yfinance
# pip install tkcalendar

import tkinter as tk
import yfinance as yf
import pandas as pd
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime


# Function to fetch stock data
def get_stock_data():
    try:
        # Fetch data from entry fields
        company_code = entry_company_code.get()
        start_date = cal_start_date.get_date()  # Fetch date from calendar
        end_date = cal_end_date.get_date()  # Fetch date from calendar
        print(f"Company: {company_code}, Start: {start_date}, End: {end_date}")

        df = yf.download(company_code, start=start_date, end=end_date)
        print(df.head())

    except ValueError:
        messagebox.showerror("Error", "Check data")


date_pattern_selected = 'yyyy-mm-dd'

# Creating the main window
root = tk.Tk()
root.title("Display Stock Info")

# Label for entering company name
label_company_code = tk.Label(root, text="Enter stock company code:")
label_company_code.pack(pady=5)

# Text entry field for entering company code
entry_company_code = tk.Entry(root, width=30)
entry_company_code.pack(pady=5)

# Label for selecting the start date
label_start_date = tk.Label(root, text="Select start date")
label_start_date.pack(pady=5)

# Calendar widget for selecting the start date
cal_start_date = Calendar(root, selectmode='day', date_pattern=date_pattern_selected)
cal_start_date.pack(pady=5)

# Label for selecting the end date
label_end_date = tk.Label(root, text="Select end date")
label_end_date.pack(pady=5)

# Calendar widget for selecting the end date
cal_end_date = Calendar(root, selectmode='day', date_pattern=date_pattern_selected)
cal_end_date.pack(pady=5)

# Button to display stock data
button_display_data = tk.Button(root, text="Display Data", command=get_stock_data)
button_display_data.pack(pady=10)

# Running the main loop
root.mainloop()
