import pandas as pd
import sqlite3 as sql

# 	Date	Ticker	Open	High	Low	Close	Volume	Dividends	ema50	ema200	yield
# 0	2023-01-05	^GSPC	3839.739990	3839.739990	3802.419922	3808.100098	3893450000
def create_db(conn: sql.Connection):
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS daily_stock_price (
                Date DATE,
                Ticker TEXT,
                Open FLOAT,
                High FLOAT,
                Low FLOAT,
                Close FLOAT,
                Volume INTEGER,
                Dividends FLOAT,
                ema50 FLOAT,
                ema200 FLOAT,
                yield FLOAT,
                PRIMARY KEY (Date, Ticker)
            )"""
        )
        conn.commit()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_data ( 
                Ticker TEXT,
                Year INTEGER,
                [Total Revenue] FLOAT,
                [Total Expenses] FLOAT,
                [Gross Profit] FLOAT,
                EBITDA FLOAT,
                [Free Cash Flow] FLOAT,
                [Common Stock Dividend Paid] FLOAT,
                [Basic EPS] FLOAT,
                PRIMARY KEY (Ticker)
            )"""
        )
        conn.commit()

def insert_to_stock_data(
        df: pd.DataFrame,
        conn: sql.Connection, 
    ):
    ticker = df['Ticker'].iloc[0]
    start_date = df['Date'].min()
    end_date = df['Date'].max()

    with conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            DELETE FROM daily_stock_price 
            WHERE Ticker = '{ticker}'
                AND Date BETWEEN '{start_date}' AND '{end_date}'
        """)
        conn.commit()

        df.to_sql(
            'daily_stock_price', 
            conn, 
            if_exists='append', 
            index=False
        )

def insert_to_financial_data(
    df: pd.DataFrame,
    ticker: str,
    conn: sql.Connection
):
    df.insert(loc=0, column='Ticker', value=ticker)

    with conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            DELETE FROM financial_data 
            WHERE Ticker = '{ticker}'
        """)
        conn.commit()

        df.to_sql(
            'financial_data', 
            conn, 
            if_exists='append', 
            index=False
        )

if __name__ == "__main__":
    create_db()