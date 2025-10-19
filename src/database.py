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
                PRIMARY KEY (Year, Ticker)
            )"""
        )
        conn.commit()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                strategy_type TEXT NOT NULL,
                parameters TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        conn.commit()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                date DATE NOT NULL,
                signal TEXT NOT NULL,
                price FLOAT,
                FOREIGN KEY (strategy_id) REFERENCES trading_strategies(id),
                UNIQUE(strategy_id, ticker, date)
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

def insert_strategy(
    name: str,
    description: str,
    strategy_type: str,
    parameters: str,
    conn: sql.Connection
):
    """Insert a new trading strategy into the database."""
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO trading_strategies 
            (name, description, strategy_type, parameters)
            VALUES (?, ?, ?, ?)
        """, (name, description, strategy_type, parameters))
        conn.commit()
        return cursor.lastrowid

def insert_strategy_signals(
    strategy_id: int,
    signals_df: pd.DataFrame,
    conn: sql.Connection
):
    """Insert strategy signals into the database.
    
    Args:
        strategy_id: ID of the strategy
        signals_df: DataFrame with columns: ticker, date, signal, price
        conn: Database connection
    """
    signals_df = signals_df.copy()
    signals_df['strategy_id'] = strategy_id
    
    with conn:
        # Delete existing signals for this strategy
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM strategy_signals 
            WHERE strategy_id = ?
        """, (strategy_id,))
        conn.commit()
        
        # Insert new signals
        signals_df[['strategy_id', 'ticker', 'date', 'signal', 'price']].to_sql(
            'strategy_signals',
            conn,
            if_exists='append',
            index=False
        )

def get_all_strategies(conn: sql.Connection) -> pd.DataFrame:
    """Retrieve all trading strategies from database."""
    return pd.read_sql("""
        SELECT id, name, description, strategy_type, parameters 
        FROM trading_strategies
    """, conn)

def get_strategy_signals(
    strategy_id: int,
    ticker: str,
    conn: sql.Connection
) -> pd.DataFrame:
    """Retrieve signals for a specific strategy and ticker."""
    return pd.read_sql("""
        SELECT date, signal, price
        FROM strategy_signals
        WHERE strategy_id = ? AND ticker = ?
        ORDER BY date
    """, conn, params=(strategy_id, ticker))

if __name__ == "__main__":
    create_db()