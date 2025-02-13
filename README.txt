Stock Price Explorer
====================

This Python application allows users to explore stock prices using **Tkinter** for the GUI and **yfinance** to fetch real-time stock data. It also includes functionality to view stock trends, export data to an **SQLite** database, and manage stored data.

Dependencies:
-------------
- Python 3.x
- yfinance
- matplotlib
- tkinter (pre-installed)
- sqlite3 (pre-installed)

Install with:
-------------
pip install yfinance matplotlib

Configuration:
--------------
There is no additional configuration required for the basic functionality. Simply run the script and interact with the GUI.

Functions:
----------
- `get_stock_data()`: Fetches stock data for a given company code and period, then displays it on a chart.
- `export_data()`: Exports stock data to an SQLite database.
- `clear_data()`: Clears the chart and deletes data from the database.
- `open_database()`: Opens a database file and displays the first 10 records.
- `clear_chart()`: Clears the chart from the window.
- `update_time()`: Updates the current time on the label every second.
- `on_closing()`: Handles the window close event.

GUI:
----
1. **Enter Stock Company Code**: Input the stock code (e.g., "AAPL").
2. **Select Time Period**: Use the slider to select the period (1–365 days).
3. **Fetch Data**: Click to fetch stock data and view it on the chart.
4. **Export Data**: Export the fetched data to an SQLite database.
5. **Open Database**: Open and view stored data from the database.

Usage:
------
1. Run the script to open the GUI.
2. Enter a stock company code (e.g., "AAPL").
3. Select a time period and fetch the data to view the stock trends.
4. Use "Export" to save data to the SQLite database.

License:
--------
MIT License
