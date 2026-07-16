import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bank_system.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create accounts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_number TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            ifsc TEXT NOT NULL,
            address TEXT NOT NULL,
            photo_path TEXT,
            balance REAL DEFAULT 0.0,
            account_type TEXT NOT NULL,
            status TEXT DEFAULT 'Active',
            created_at TEXT NOT NULL
        )
    ''')
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            reference_account TEXT,
            timestamp TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (account_number) REFERENCES accounts (account_number)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_account(account_number, name, ifsc, address, photo_path, initial_balance, account_type):
    conn = get_connection()
    cursor = conn.cursor()
    
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        cursor.execute('''
            INSERT INTO accounts (account_number, name, ifsc, address, photo_path, balance, account_type, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Active', ?)
        ''', (account_number, name, ifsc, address, photo_path, initial_balance, account_type, created_at))
        
        # Log initial deposit as transaction if > 0
        if initial_balance > 0:
            cursor.execute('''
                INSERT INTO transactions (account_number, type, amount, reference_account, timestamp, description)
                VALUES (?, 'Deposit', ?, NULL, ?, 'Initial Deposit')
            ''', (account_number, initial_balance, created_at))
            
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Account number already exists!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_account(account_number, name, ifsc, address, photo_path, status):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE accounts
            SET name = ?, ifsc = ?, address = ?, photo_path = ?, status = ?
            WHERE account_number = ?
        ''', (name, ifsc, address, photo_path, status, account_number))
        conn.commit()
        if cursor.rowcount == 0:
            return False, "Account not found!"
        return True, "Account updated successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_account(account_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM accounts WHERE account_number = ?', (account_number,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_accounts(search_query=None):
    conn = get_connection()
    cursor = conn.cursor()
    if search_query:
        # Search in name or account number
        q = f"%{search_query}%"
        cursor.execute('SELECT * FROM accounts WHERE name LIKE ? OR account_number LIKE ? ORDER BY name ASC', (q, q))
    else:
        cursor.execute('SELECT * FROM accounts ORDER BY name ASC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def deposit(account_number, amount, description="Deposit"):
    if amount <= 0:
        return False, "Amount must be greater than zero!"
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if active
        cursor.execute('SELECT status, balance FROM accounts WHERE account_number = ?', (account_number,))
        row = cursor.fetchone()
        if not row:
            return False, "Account not found!"
        if row['status'] != 'Active':
            return False, f"Account is {row['status']}. Deposits not allowed."
        
        new_balance = row['balance'] + amount
        cursor.execute('UPDATE accounts SET balance = ? WHERE account_number = ?', (new_balance, account_number))
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO transactions (account_number, type, amount, reference_account, timestamp, description)
            VALUES (?, 'Deposit', ?, NULL, ?, ?)
        ''', (account_number, amount, timestamp, description))
        
        conn.commit()
        return True, f"Deposited ${amount:.2f} successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def withdraw(account_number, amount, description="Withdrawal"):
    if amount <= 0:
        return False, "Amount must be greater than zero!"
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if active & has enough balance
        cursor.execute('SELECT status, balance FROM accounts WHERE account_number = ?', (account_number,))
        row = cursor.fetchone()
        if not row:
            return False, "Account not found!"
        if row['status'] != 'Active':
            return False, f"Account is {row['status']}. Withdrawals not allowed."
        if row['balance'] < amount:
            return False, "Insufficient balance!"
        
        new_balance = row['balance'] - amount
        cursor.execute('UPDATE accounts SET balance = ? WHERE account_number = ?', (new_balance, account_number))
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO transactions (account_number, type, amount, reference_account, timestamp, description)
            VALUES (?, 'Withdrawal', ?, NULL, ?, ?)
        ''', (account_number, amount, timestamp, description))
        
        conn.commit()
        return True, f"Withdrew ${amount:.2f} successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def transfer(from_account, to_account, amount, description="Transfer"):
    if amount <= 0:
        return False, "Amount must be greater than zero!"
    if from_account == to_account:
        return False, "Source and destination accounts must be different!"
        
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check source account
        cursor.execute('SELECT status, balance FROM accounts WHERE account_number = ?', (from_account,))
        source = cursor.fetchone()
        if not source:
            return False, "Source account not found!"
        if source['status'] != 'Active':
            return False, f"Source account is {source['status']}. Transfers not allowed."
        if source['balance'] < amount:
            return False, "Insufficient balance in source account!"
            
        # Check destination account
        cursor.execute('SELECT status, balance FROM accounts WHERE account_number = ?', (to_account,))
        dest = cursor.fetchone()
        if not dest:
            return False, "Destination account not found!"
        if dest['status'] != 'Active':
            return False, f"Destination account is {dest['status']}. Transfers not allowed."
            
        # Update source
        new_source_balance = source['balance'] - amount
        cursor.execute('UPDATE accounts SET balance = ? WHERE account_number = ?', (new_source_balance, from_account))
        
        # Update dest
        new_dest_balance = dest['balance'] + amount
        cursor.execute('UPDATE accounts SET balance = ? WHERE account_number = ?', (new_dest_balance, to_account))
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Log source transaction
        cursor.execute('''
            INSERT INTO transactions (account_number, type, amount, reference_account, timestamp, description)
            VALUES (?, 'Transfer (Out)', ?, ?, ?, ?)
        ''', (from_account, amount, to_account, timestamp, description))
        
        # Log dest transaction
        cursor.execute('''
            INSERT INTO transactions (account_number, type, amount, reference_account, timestamp, description)
            VALUES (?, 'Transfer (In)', ?, ?, ?, ?)
        ''', (to_account, amount, from_account, timestamp, description))
        
        conn.commit()
        return True, f"Transferred ${amount:.2f} to Account {to_account} successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_transactions(account_number=None, limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    if account_number:
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE account_number = ? 
            ORDER BY datetime(timestamp) DESC 
            LIMIT ?
        ''', (account_number, limit))
    else:
        cursor.execute('''
            SELECT * FROM transactions 
            ORDER BY datetime(timestamp) DESC 
            LIMIT ?
        ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM accounts')
    total_accounts = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(balance) FROM accounts WHERE status = "Active"')
    total_balance = cursor.fetchone()[0] or 0.0
    
    cursor.execute('SELECT COUNT(*) FROM transactions')
    total_transactions = cursor.fetchone()[0]
    
    conn.close()
    return {
        'total_accounts': total_accounts,
        'total_balance': total_balance,
        'total_transactions': total_transactions
    }
