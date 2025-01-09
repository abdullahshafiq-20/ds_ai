from datetime import datetime
from typing import Dict, List, Optional, Tuple
import random
import hashlib
from abc import ABC, abstractmethod
from enum import Enum
import re

class AccountType(Enum):
    SAVINGS = "Savings"
    CURRENT = "Current"

class TransactionType(Enum):
    DEPOSIT = "Deposit"
    WITHDRAWAL = "Withdrawal"
    TRANSFER_SENT = "Transfer Sent"
    TRANSFER_RECEIVED = "Transfer Received"
    INTEREST_CREDIT = "Interest Credit"

class BankingError(Exception):
    """Custom exception for banking operations"""
    pass

class Account(ABC):
    def __init__(self, account_number: str, account_holder: str, account_type: AccountType):
        self._account_number: str = account_number
        self._account_holder: str = account_holder
        self._balance: float = 0.0
        self._transactions: List[Dict] = []
        self._account_type: AccountType = account_type
        self._is_active: bool = True
        
    @abstractmethod
    def calculate_interest(self) -> float:
        """Calculate interest based on account type"""
        pass

    def deposit(self, amount: float) -> bool:
        """
        Deposit money into the account.
        
        Args:
            amount (float): Amount to deposit
            
        Returns:
            bool: True if deposit successful, False otherwise
            
        Raises:
            BankingError: If amount is invalid or account is inactive
        """
        if not self._is_active:
            raise BankingError("Account is inactive")
            
        if amount <= 0:
            raise BankingError("Invalid deposit amount")
        
        self._balance += amount
        self._add_transaction(TransactionType.DEPOSIT, amount)
        return True
        
    def withdraw(self, amount: float) -> bool:
        """
        Withdraw money from the account.
        
        Args:
            amount (float): Amount to withdraw
            
        Returns:
            bool: True if withdrawal successful, False otherwise
            
        Raises:
            BankingError: If insufficient balance or invalid amount
        """
        if not self._is_active:
            raise BankingError("Account is inactive")
            
        if amount <= 0:
            raise BankingError("Invalid withdrawal amount")
            
        if amount > self._balance:
            raise BankingError("Insufficient balance")
        
        self._balance -= amount
        self._add_transaction(TransactionType.WITHDRAWAL, -amount)
        return True
    
    def get_balance(self) -> float:
        """Return current balance."""
        return self._balance
        
    def _add_transaction(self, transaction_type: TransactionType, amount: float):
        """Add a transaction to the transaction history."""
        transaction = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': transaction_type.value,
            'amount': amount,
            'balance': self._balance
        }
        self._transactions.append(transaction)
        
    def get_statement(self) -> Tuple[str, List[Dict]]:
        """
        Get account statement.
        
        Returns:
            Tuple containing account info and list of transactions
        """
        account_info = (
            f"Account Statement for {self._account_holder}\n"
            f"Account Number: {self._account_number}\n"
            f"Account Type: {self._account_type.value}\n"
            f"Account Status: {'Active' if self._is_active else 'Inactive'}"
        )
        return account_info, self._transactions
    
    @property
    def account_number(self) -> str:
        return self._account_number
    
    @property
    def account_holder(self) -> str:
        return self._account_holder
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    def toggle_account_status(self):
        """Toggle account between active and inactive states."""
        self._is_active = not self._is_active

class SavingsAccount(Account):
    INTEREST_RATE = 0.045  # 4.5% annual interest rate
    MINIMUM_BALANCE = 1000.0
    
    def __init__(self, account_number: str, account_holder: str):
        super().__init__(account_number, account_holder, AccountType.SAVINGS)
        
    def calculate_interest(self) -> float:
        """Calculate monthly interest for savings account."""
        monthly_interest = (self._balance * self.INTEREST_RATE) / 12
        self._balance += monthly_interest
        self._add_transaction(TransactionType.INTEREST_CREDIT, monthly_interest)
        return monthly_interest
    
    def withdraw(self, amount: float) -> bool:
        """Override withdraw to enforce minimum balance."""
        if (self._balance - amount) < self.MINIMUM_BALANCE:
            raise BankingError(f"Must maintain minimum balance of {self.MINIMUM_BALANCE}")
        return super().withdraw(amount)

class CurrentAccount(Account):
    OVERDRAFT_LIMIT = 10000.0
    
    def __init__(self, account_number: str, account_holder: str):
        super().__init__(account_number, account_holder, AccountType.CURRENT)
        
    def calculate_interest(self) -> float:
        """Current accounts don't earn interest."""
        return 0.0
    
    def withdraw(self, amount: float) -> bool:
        """Override withdraw to allow overdraft up to limit."""
        if (self._balance - amount) < -self.OVERDRAFT_LIMIT:
            raise BankingError(f"Exceeds overdraft limit of {self.OVERDRAFT_LIMIT}")
        return super().withdraw(amount)

class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password_hash = self._hash_password(password)
        
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify if provided password matches stored hash."""
        return self._hash_password(password) == self.password_hash

class Bank:
    def __init__(self):
        self._accounts: Dict[str, Account] = {}
        self._users: Dict[str, User] = {}
        self._account_holders: Dict[str, List[str]] = {}  # username -> account numbers
        
    def _validate_name(self, name: str) -> bool:
        """Validate account holder name."""
        return bool(re.match(r'^[A-Za-z\s]{2,50}$', name))
    
    def _validate_username(self, username: str) -> bool:
        """Validate username."""
        return bool(re.match(r'^[A-Za-z0-9_]{4,20}$', username))
    
    def _validate_password(self, password: str) -> bool:
        """
        Validate password strength:
        - At least 8 characters
        - Contains uppercase and lowercase letters
        - Contains numbers
        - Contains special characters
        """
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'[0-9]', password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        return True
        
    def _generate_account_number(self) -> str:
        """Generate a unique 10-digit account number."""
        while True:
            account_number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            if account_number not in self._accounts:
                return account_number
    
    def create_user(self, username: str, password: str) -> bool:
        """
        Create a new user account.
        
        Args:
            username (str): Desired username
            password (str): User's password
            
        Returns:
            bool: True if user created successfully
            
        Raises:
            BankingError: If validation fails or user exists
        """
        if not self._validate_username(username):
            raise BankingError("Invalid username format")
        if not self._validate_password(password):
            raise BankingError("Password does not meet security requirements")
        if username in self._users:
            raise BankingError("Username already exists")
            
        self._users[username] = User(username, password)
        self._account_holders[username] = []
        return True
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user credentials."""
        user = self._users.get(username)
        if user and user.verify_password(password):
            return True
        return False
    
    def open_account(self, username: str, account_holder: str, account_type: AccountType) -> str:
        """
        Create a new bank account.
        
        Args:
            username (str): Username of account owner
            account_holder (str): Name of account holder
            account_type (AccountType): Type of account to create
            
        Returns:
            str: New account number
            
        Raises:
            BankingError: If validation fails
        """
        if not self._validate_name(account_holder):
            raise BankingError("Invalid account holder name")
        
        account_number = self._generate_account_number()
        
        if account_type == AccountType.SAVINGS:
            account = SavingsAccount(account_number, account_holder)
        else:
            account = CurrentAccount(account_number, account_holder)
            
        self._accounts[account_number] = account
        self._account_holders[username].append(account_number)
        return account_number
    
    def get_account(self, account_number: str) -> Optional[Account]:
        """Retrieve an account by its account number."""
        return self._accounts.get(account_number)
    
    def get_user_accounts(self, username: str) -> List[str]:
        """Get all account numbers associated with a username."""
        return self._account_holders.get(username, [])
    
    def transfer(self, sender_account_number: str, receiver_account_number: str, amount: float) -> bool:
        """
        Transfer money between two accounts.
        
        Args:
            sender_account_number (str): Sender's account number
            receiver_account_number (str): Receiver's account number
            amount (float): Amount to transfer
            
        Returns:
            bool: True if transfer successful
            
        Raises:
            BankingError: If transfer fails
        """
        if amount <= 0:
            raise BankingError("Invalid transfer amount")
            
        sender = self.get_account(sender_account_number)
        receiver = self.get_account(receiver_account_number)
        
        if not sender or not receiver:
            raise BankingError("Invalid account number(s)")
            
        if not sender.is_active or not receiver.is_active:
            raise BankingError("One or both accounts are inactive")
        
        # Perform transfer
        sender.withdraw(amount)
        receiver.deposit(amount)
        
        # Record transfer transactions
        sender._add_transaction(TransactionType.TRANSFER_SENT, -amount)
        receiver._add_transaction(TransactionType.TRANSFER_RECEIVED, amount)
        return True
    
    def calculate_all_interest(self):
        """Calculate and apply interest for all savings accounts."""
        for account in self._accounts.values():
            if isinstance(account, SavingsAccount) and account.is_active:
                account.calculate_interest()
    
    def admin_check_total_deposit(self) -> float:
        """Return total balance of all accounts."""
        return sum(account.get_balance() for account in self._accounts.values())
    
    def admin_check_total_accounts(self) -> int:
        """Return total number of accounts."""
        return len(self._accounts)
    
    def admin_get_account_stats(self) -> Dict:
        """Get detailed statistics about accounts."""
        total_accounts = len(self._accounts)
        active_accounts = sum(1 for acc in self._accounts.values() if acc.is_active)
        savings_accounts = sum(1 for acc in self._accounts.values() 
                             if isinstance(acc, SavingsAccount))
        current_accounts = sum(1 for acc in self._accounts.values() 
                             if isinstance(acc, CurrentAccount))
        
        return {
            "total_accounts": total_accounts,
            "active_accounts": active_accounts,
            "inactive_accounts": total_accounts - active_accounts,
            "savings_accounts": savings_accounts,
            "current_accounts": current_accounts,
            "total_deposits": self.admin_check_total_deposit()
        }

def main():
    bank = Bank()
    
    def print_menu(menu_items: Dict[str, str]):
        """Print formatted menu."""
        print("\n" + "=" * 40)
        for key, value in menu_items.items():
            print(f"{key}. {value}")
        print("=" * 40)
    
    def get_validated_input(prompt: str, validation_func=None, error_msg: str = None) -> str:
        """Get and validate user input."""
        while True:
            value = input(prompt).strip()
            if not validation_func or validation_func(value):
                return value
            print(error_msg or "Invalid input, please try again.")
    
    # Menu definitions
    main_menu = {
        "1": "Register New User",
        "2": "User Login",
        "3": "Admin Login",
        "4": "Exit"
    }
    
    user_menu = {
        "1": "Open New Account",
        "2": "View My Accounts",
        "3": "Deposit Money",
        "4": "Withdraw Money",
        "5": "Check Balance",
        "6": "Transfer Money",
        "7": "Print Statement",
        "8": "Logout"
    }
    
    admin_menu = {
        "1": "View Total Deposits",
        "2": "View Account Statistics",
        "3": "Calculate Monthly Interest",
        "4": "Toggle Account Status",
        "5": "Logout"
    }
    
    while True:
        print_menu(main_menu)
        choice = input("Enter your choice: ")
        
        if choice == "1":  # Register New User
            try:
                username = get_validated_input(
                    "Enter username: ",
                    bank._validate_username,
                    "Username must be 4-20 characters long and contain only letters, numbers, and underscores."
                )
                password = get_validated_input(
                    "Enter password: ",
                    bank._validate_password,
                    "Password must be at least 8 characters long and contain uppercase, lowercase, numbers, and special characters."
                )
                if bank.create_user(username, password):
                    print("User registered successfully!")
            except BankingError as e:
                print(f"Error: {e}")
        
        elif choice == "2":  # User Login
            username = input("Enter username: ")
            password = input("Enter password: ")
            
            if bank.authenticate_user(username, password):
                print("Login successful!")
                while True:
                    print_menu(user_menu)
                    user_choice = input("Enter your choice: ")
                    
                    try:
                        if user_choice == "1":  # Open New Account
                            name = get_validated_input(
                                "Enter account holder name: ",
                                bank._validate_name,
                                "Name must be 2-50 characters long and contain only letters and spaces."
                            )
                            print("\nSelect Account Type:")
                            print("1. Savings Account")
                            print("2. Current Account")
                            acc_type = input("Enter choice (1/2): ")
                            
                            account_type = AccountType.SAVINGS if acc_type == "1" else AccountType.CURRENT
                            account_number = bank.open_account(username, name, account_type)
                            print(f"Account created successfully! Your account number is: {account_number}")
                        
                        elif user_choice == "2":  # View My Accounts
                            accounts = bank.get_user_accounts(username)
                            if not accounts:
                                print("You don't have any accounts yet.")
                            else:
                                print("\nYour Accounts:")
                                for acc_num in accounts:
                                    account = bank.get_account(acc_num)
                                    print(f"Account Number: {acc_num}")
                                    print(f"Type: {account._account_type.value}")
                                    print(f"Balance: ${account.get_balance():.2f}")
                                    print(f"Status: {'Active' if account.is_active else 'Inactive'}\n")
                        
                        elif user_choice == "3":  # Deposit Money
                            account_number = input("Enter account number: ")
                            account = bank.get_account(account_number)
                            if account:
                                amount = float(input("Enter amount to deposit: $"))
                                account.deposit(amount)
                                print("Deposit successful!")
                            else:
                                print("Account not found!")
                        
                        elif user_choice == "4":  # Withdraw Money
                            account_number = input("Enter account number: ")
                            account = bank.get_account(account_number)
                            if account:
                                amount = float(input("Enter amount to withdraw: $"))
                                account.withdraw(amount)
                                print("Withdrawal successful!")
                            else:
                                print("Account not found!")
                        
                        elif user_choice == "5":  # Check Balance
                            account_number = input("Enter account number: ")
                            account = bank.get_account(account_number)
                            if account:
                                print(f"Current balance: ${account.get_balance():.2f}")
                            else:
                                print("Account not found!")
                        
                        elif user_choice == "6":  # Transfer Money
                            sender_account = input("Enter your account number: ")
                            receiver_account = input("Enter recipient's account number: ")
                            amount = float(input("Enter amount to transfer: $"))
                            bank.transfer(sender_account, receiver_account, amount)
                            print("Transfer successful!")
                        
                        elif user_choice == "7":  # Print Statement
                            account_number = input("Enter account number: ")
                            account = bank.get_account(account_number)
                            if account:
                                account_info, transactions = account.get_statement()
                                print("\n" + "=" * 80)
                                print(account_info)
                                print("=" * 80)
                                print(f"{'