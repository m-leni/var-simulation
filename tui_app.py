"""
Terminal User Interface (TUI) for stock analysis using Textual.
This is a proof of concept implementing the stock analysis view from the Streamlit app.

Entry point for the TUI application. All TUI components are in src/tui.py module.
"""
from src.tui import run_tui


def main():
    """Run the TUI application."""
    run_tui()


if __name__ == "__main__":
    main()
