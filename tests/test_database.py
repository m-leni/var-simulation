"""
Unit tests for src/database.py module.
"""
import pandas as pd
from src.database import create_db, insert_to_stock_data, insert_to_financial_data


class TestCreateDB:
    """Tests for create_db function."""
    
    def test_creates_tables(self, in_memory_db):
        """Test that database tables are created."""
        create_db(in_memory_db)
        
        # Check if daily_stock_price table exists
        cursor = in_memory_db.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='daily_stock_price'
        """)
        assert cursor.fetchone() is not None
        
        # Check if financial_data table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='financial_data'
        """)
        assert cursor.fetchone() is not None
        
    def test_table_schema_stock_price(self, in_memory_db):
        """Test daily_stock_price table schema."""
        create_db(in_memory_db)
        cursor = in_memory_db.cursor()
        cursor.execute("PRAGMA table_info(daily_stock_price)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_columns = {
            'Date': 'DATE',
            'Ticker': 'TEXT',
            'Open': 'FLOAT',
            'High': 'FLOAT',
            'Low': 'FLOAT',
            'Close': 'FLOAT',
            'Volume': 'INTEGER',
            'Dividends': 'FLOAT',
            'ema50': 'FLOAT',
            'ema200': 'FLOAT',
            'yield': 'FLOAT'
        }
        
        for col, dtype in expected_columns.items():
            assert col in columns
            assert columns[col] == dtype
            
    def test_table_schema_financial_data(self, in_memory_db):
        """Test financial_data table schema."""
        create_db(in_memory_db)
        cursor = in_memory_db.cursor()
        cursor.execute("PRAGMA table_info(financial_data)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_columns = {
            'Ticker': 'TEXT',
            'Year': 'INTEGER',
            'Total Revenue': 'FLOAT',
            'Total Expenses': 'FLOAT',
            'Gross Profit': 'FLOAT',
            'EBITDA': 'FLOAT',
            'Free Cash Flow': 'FLOAT',
            'Common Stock Dividend Paid': 'FLOAT',
            'Basic EPS': 'FLOAT'
        }
        
        for col in expected_columns.keys():
            assert col in columns
            
    def test_idempotent(self, in_memory_db):
        """Test that create_db can be called multiple times without error."""
        create_db(in_memory_db)
        create_db(in_memory_db)  # Should not raise error
        
        cursor = in_memory_db.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name='daily_stock_price'
        """)
        assert cursor.fetchone()[0] == 1  # Should only have one table


class TestInsertToStockData:
    """Tests for insert_to_stock_data function."""
    
    def test_insert_new_data(self, in_memory_db, sample_stock_data):
        """Test inserting new stock data."""
        create_db(in_memory_db)
        insert_to_stock_data(sample_stock_data, in_memory_db)
        
        # Verify data was inserted
        df = pd.read_sql("SELECT * FROM daily_stock_price", in_memory_db)
        assert len(df) == len(sample_stock_data)
        assert df['Ticker'].iloc[0] == 'AAPL'
        
    def test_replace_existing_data(self, in_memory_db, sample_stock_data):
        """Test that existing data is replaced."""
        create_db(in_memory_db)
        
        # Insert original data
        insert_to_stock_data(sample_stock_data, in_memory_db)
        
        # Modify data and insert again
        modified_data = sample_stock_data.copy()
        modified_data['Close'] = modified_data['Close'] * 1.1
        insert_to_stock_data(modified_data, in_memory_db)
        
        # Verify data was updated
        df = pd.read_sql("SELECT * FROM daily_stock_price", in_memory_db)
        assert len(df) == len(sample_stock_data)  # Same number of rows
        assert df['Close'].iloc[0] == modified_data['Close'].iloc[0]
        
    def test_date_range_deletion(self, in_memory_db):
        """Test that only data in date range is deleted."""
        create_db(in_memory_db)
        
        # Insert data for two different date ranges
        dates1 = pd.date_range(start='2024-01-01', periods=5, freq='D')
        df1 = pd.DataFrame({
            'Date': dates1,
            'Ticker': ['AAPL'] * 5,
            'Open': [100] * 5,
            'High': [101] * 5,
            'Low': [99] * 5,
            'Close': [100] * 5,
            'Volume': [1000000] * 5,
            'Dividends': [0] * 5,
            'ema50': [100] * 5,
            'ema200': [99] * 5,
            'yield': [0] * 5
        })
        
        dates2 = pd.date_range(start='2024-02-01', periods=5, freq='D')
        df2 = pd.DataFrame({
            'Date': dates2,
            'Ticker': ['AAPL'] * 5,
            'Open': [110] * 5,
            'High': [111] * 5,
            'Low': [109] * 5,
            'Close': [110] * 5,
            'Volume': [1000000] * 5,
            'Dividends': [0] * 5,
            'ema50': [110] * 5,
            'ema200': [109] * 5,
            'yield': [0] * 5
        })
        
        insert_to_stock_data(df1, in_memory_db)
        insert_to_stock_data(df2, in_memory_db)
        
        # Should have both ranges
        df = pd.read_sql("SELECT * FROM daily_stock_price", in_memory_db)
        assert len(df) == 10
        
    def test_multiple_tickers(self, in_memory_db):
        """Test inserting data for multiple tickers."""
        create_db(in_memory_db)
        
        dates = pd.date_range(start='2024-01-01', periods=5, freq='D')
        
        for ticker in ['AAPL', 'GOOGL', 'MSFT']:
            df = pd.DataFrame({
                'Date': dates,
                'Ticker': [ticker] * 5,
                'Open': [100] * 5,
                'High': [101] * 5,
                'Low': [99] * 5,
                'Close': [100] * 5,
                'Volume': [1000000] * 5,
                'Dividends': [0] * 5,
                'ema50': [100] * 5,
                'ema200': [99] * 5,
                'yield': [0] * 5
            })
            insert_to_stock_data(df, in_memory_db)
        
        # Should have data for all tickers
        df = pd.read_sql("SELECT DISTINCT Ticker FROM daily_stock_price", in_memory_db)
        assert len(df) == 3


class TestInsertToFinancialData:
    """Tests for insert_to_financial_data function."""
    
    def test_insert_new_data(self, in_memory_db, sample_financial_data):
        """Test inserting new financial data."""
        create_db(in_memory_db)
        insert_to_financial_data(sample_financial_data.copy(), 'AAPL', in_memory_db)
        
        # Verify data was inserted
        df = pd.read_sql("SELECT * FROM financial_data WHERE Ticker='AAPL'", in_memory_db)
        assert len(df) == len(sample_financial_data)
        assert df['Ticker'].iloc[0] == 'AAPL'
        
    def test_ticker_column_added(self, in_memory_db, sample_financial_data):
        """Test that ticker column is added to DataFrame."""
        create_db(in_memory_db)
        df_copy = sample_financial_data.copy()
        assert 'Ticker' not in df_copy.columns
        
        insert_to_financial_data(df_copy, 'AAPL', in_memory_db)
        
        # Verify ticker was added to database
        df = pd.read_sql("SELECT * FROM financial_data", in_memory_db)
        assert 'Ticker' in df.columns
        assert all(df['Ticker'] == 'AAPL')
        
    def test_replace_existing_data(self, in_memory_db, sample_financial_data):
        """Test that existing financial data is replaced."""
        create_db(in_memory_db)
        
        # Insert original data
        insert_to_financial_data(sample_financial_data.copy(), 'AAPL', in_memory_db)
        
        # Modify and insert again
        modified_data = sample_financial_data.copy()
        modified_data['Total Revenue'] = modified_data['Total Revenue'] * 1.2
        insert_to_financial_data(modified_data, 'AAPL', in_memory_db)
        
        # Verify data was updated
        df = pd.read_sql("SELECT * FROM financial_data WHERE Ticker='AAPL'", in_memory_db)
        assert len(df) == len(sample_financial_data)
        assert df['Total Revenue'].iloc[0] == modified_data['Total Revenue'].iloc[0]
        
    def test_multiple_tickers(self, in_memory_db, sample_financial_data):
        """Test inserting financial data for multiple tickers."""
        create_db(in_memory_db)
        
        for ticker in ['AAPL', 'GOOGL', 'MSFT']:
            insert_to_financial_data(sample_financial_data.copy(), ticker, in_memory_db)
        
        # Should have data for all tickers
        df = pd.read_sql("SELECT DISTINCT Ticker FROM financial_data", in_memory_db)
        assert len(df) == 3
        
    def test_delete_before_insert(self, in_memory_db, sample_financial_data):
        """Test that old data is deleted before new data is inserted."""
        create_db(in_memory_db)
        
        # Insert initial data
        insert_to_financial_data(sample_financial_data.copy(), 'AAPL', in_memory_db)
        initial_count = len(pd.read_sql("SELECT * FROM financial_data WHERE Ticker='AAPL'", in_memory_db))
        
        # Insert fewer rows
        fewer_data = sample_financial_data.iloc[:2].copy()
        insert_to_financial_data(fewer_data, 'AAPL', in_memory_db)
        
        # Should only have the new data
        df = pd.read_sql("SELECT * FROM financial_data WHERE Ticker='AAPL'", in_memory_db)
        assert len(df) == 2
        assert initial_count == len(df)
