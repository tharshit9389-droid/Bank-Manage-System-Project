import csv
import os
from database import get_all_accounts, get_transactions, get_account

def export_accounts_to_csv(filepath):
    """Export all accounts to a CSV file."""
    accounts = get_all_accounts()
    if not accounts:
        return False, "No accounts to export."
        
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write headers
            writer.writerow(["Account Number", "Name", "IFSC Code", "Address", "Account Type", "Balance ($)", "Status", "Created At"])
            # Write data rows
            for acc in accounts:
                writer.writerow([
                    acc['account_number'],
                    acc['name'],
                    acc['ifsc'],
                    acc['address'],
                    acc['account_type'],
                    f"{acc['balance']:.2f}",
                    acc['status'],
                    acc['created_at']
                ])
        return True, f"Accounts successfully exported to:\n{filepath}"
    except Exception as e:
        return False, str(e)

def export_transactions_to_csv(filepath):
    """Export all transaction history to a CSV file."""
    transactions = get_transactions(limit=1000000) # Fetch all transactions
    if not transactions:
        return False, "No transactions to export."
        
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write headers
            writer.writerow(["Transaction ID", "Account Number", "Type", "Amount ($)", "Reference Account", "Timestamp", "Description"])
            # Write data rows
            for tx in transactions:
                ref = tx['reference_account'] if tx['reference_account'] else "N/A"
                writer.writerow([
                    tx['id'],
                    tx['account_number'],
                    tx['type'],
                    f"{tx['amount']:.2f}",
                    ref,
                    tx['timestamp'],
                    tx['description']
                ])
        return True, f"Transactions ledger successfully exported to:\n{filepath}"
    except Exception as e:
        return False, str(e)

def export_statement_to_csv(account_number, filepath):
    """Export a specific account's details and transaction statement to CSV."""
    acc = get_account(account_number)
    if not acc:
        return False, f"Account {account_number} not found."
        
    txs = get_transactions(account_number=account_number, limit=1000000)
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Account details section
            writer.writerow(["ACCOUNT STATEMENT"])
            writer.writerow([])
            writer.writerow(["Account Number", acc['account_number']])
            writer.writerow(["Holder Name", acc['name']])
            writer.writerow(["IFSC Code", acc['ifsc']])
            writer.writerow(["Address", acc['address']])
            writer.writerow(["Account Type", acc['account_type']])
            writer.writerow(["Current Balance ($)", f"{acc['balance']:.2f}"])
            writer.writerow(["Status", acc['status']])
            writer.writerow(["Opened Date", acc['created_at']])
            writer.writerow([])
            
            # Transactions section
            writer.writerow(["TRANSACTION HISTORY"])
            writer.writerow(["Transaction ID", "Type", "Amount ($)", "Reference Account", "Timestamp", "Description"])
            
            for tx in txs:
                ref = tx['reference_account'] if tx['reference_account'] else "N/A"
                writer.writerow([
                    tx['id'],
                    tx['type'],
                    f"{tx['amount']:.2f}",
                    ref,
                    tx['timestamp'],
                    tx['description']
                ])
        return True, f"Statement for {account_number} successfully exported to:\n{filepath}"
    except Exception as e:
        return False, str(e)
