"""
TUI Screenshot Documentation
This file shows what the TUI looks like when running.
"""

TUI_SCREENSHOT = """
================================================================================
                          STOCK ANALYSIS TUI - TEXTUAL
================================================================================

┌──────────────────────────────────────────────────────────────────────────────┐
│ Stock Analysis - TUI                                                         │
│                                                                              │
│ Enter a stock ticker and number of days:                                    │
│                                                                              │
│ ┌────────────────────────────────────────────────────────────────────────┐  │
│ │  AAPL                                                                  │  │
│ └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│ ┌────────────────────────────────────────────────────────────────────────┐  │
│ │  252                                                                   │  │
│ └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  [Fetch Data]  [Clear]                                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ AAPL - Stock Metrics                                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                              │
│ Latest Price:      $150.25                                                   │
│ Price Change:      +$5.32 (+3.67%)                                           │
│ Volume:            87,234,567                                                │
│ Avg Volume:        102,456,789                                               │
│ Period High:       $155.80                                                   │
│ Period Low:        $142.10                                                   │
│ Date Range:        2024-01-15 to 2024-12-31                                  │
│ Total Records:     252                                                       │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│ Date         Open      High      Low       Close     Volume                 │
│ ──────────────────────────────────────────────────────────────────────────  │
│ 2024-12-02   148.50    150.20    147.80    149.95    85,234,567             │
│ 2024-12-03   150.00    151.50    149.50    150.80    90,123,456             │
│ 2024-12-04   150.75    152.00    150.00    151.20    88,456,789             │
│ 2024-12-05   151.30    152.80    150.90    152.10    92,345,678             │
│ 2024-12-06   152.00    153.50    151.50    152.90    87,654,321             │
│ ...                                                                          │
│ 2024-12-29   149.00    150.50    148.50    150.00    89,234,567             │
│ 2024-12-30   150.20    151.80    149.80    150.50    91,345,678             │
│ 2024-12-31   150.45    151.25    149.90    150.25    87,234,567             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

Keyboard Shortcuts:  q=Quit  r=Refresh  Tab=Navigate  Enter=Submit

================================================================================

FEATURES:
---------
✓ Interactive Input Fields     - Enter ticker symbols and date ranges
✓ Real-time Data Fetching       - Connects to Yahoo Finance API
✓ Database Caching              - Stores data in SQLite for fast access
✓ Rich Metrics Display          - Price, volume, high/low, changes
✓ Scrollable Data Table         - View detailed OHLCV data
✓ Keyboard Navigation           - Full keyboard control
✓ Clean Terminal UI             - Modern textual-based interface

USAGE:
------
1. Run: python tui_app.py
2. Enter a stock ticker (e.g., AAPL, MSFT, GOOGL)
3. Enter number of days for historical data (1-500)
4. Press Tab to move between fields
5. Click "Fetch Data" button or press Enter
6. View metrics and data table
7. Press 'r' to refresh or 'q' to quit

COMPARISON WITH STREAMLIT APP:
-------------------------------
The TUI provides the same core stock analysis functionality as the Streamlit
web interface, but in a terminal-based format. This is ideal for:
- Server environments without GUI
- SSH sessions
- Users who prefer terminal interfaces
- Lightweight, fast data analysis
- CI/CD pipelines and automation

================================================================================
"""

if __name__ == "__main__":
    print(TUI_SCREENSHOT)
