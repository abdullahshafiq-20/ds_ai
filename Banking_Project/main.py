"""
Banking System with Sleek UI using CustomTkinter

This module provides a graphical user interface (GUI) for a simple banking system.
Users can create accounts, deposit money, withdraw money, check balances, and view transaction statements.
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, List, Tuple

# Configure CustomTkinter
ctk.set_appearance_mode("System")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

# Custom Exceptions
class InvalidAmountError(Exception):
    """Raised when an invalid amount is provided (e.g., negative amount)."""
    pass

class InsufficientBalanceError(Exception):
    """Raised when there is insufficient balance for a withdrawal."""
    pass

# Banking System Functions
class Account:
    def __init__(self, name: str, initial_balance: float = 0.0):
        """
        Initializes a new account with the given name and initial balance.

        :param name: Account holder's name
        :param initial_balance: Initial balance (default is 0.0)
        """
        if initial_balance < 0:
            raise InvalidAmountError("Initial balance cannot be negative.")

        self.name = name
        self.balance = initial_balance
        self.transactions = []

    def deposit(self, amount: float) -> None:
        """
        Deposits money into the account.

        :param amount: Amount to deposit
        :raises InvalidAmountError: If the deposit amount is not positive
        """
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive.")

        self.balance += amount
        self.transactions.append(("Deposit", amount))

    def withdraw(self, amount: float) -> None:
        """
        Withdraws money from the account.

        :param amount: Amount to withdraw
        :raises InvalidAmountError: If the withdrawal amount is not positive
        :raises InsufficientBalanceError: If the account balance is insufficient
        """
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive.")
        if self.balance < amount:
            raise InsufficientBalanceError("Insufficient balance for withdrawal.")

        self.balance -= amount
        self.transactions.append(("Withdrawal", amount))

    def check_balance(self) -> float:
        """
        Returns the current balance of the account.

        :return: Current balance
        """
        return self.balance

    def print_statement(self) -> str:
        """
        Generates the transaction statement for the account.

        :return: Formatted transaction statement
        """
        statement = f"Account statement for {self.name}:\n"
        if not self.transactions:
            statement += "No transactions yet."
        else:
            balance = 0.0
            for transaction in self.transactions:
                transaction_type, amount = transaction
                if transaction_type == "Deposit":
                    balance += amount
                elif transaction_type == "Withdrawal":
                    balance -= amount
                statement += f"- {transaction_type}: ${amount:.2f}. New Balance: ${balance:.2f}.\n"
        return statement

# GUI Application
class BankingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Banking System")
        self.geometry("500x700")
        self.account = None

        # Create UI Elements
        self.create_widgets()

    def create_widgets(self):
        """Creates and places all UI elements."""
        # Title Label
        self.title_label = ctk.CTkLabel(self, text="Banking System", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=10)

        # Name Entry
        self.name_label = ctk.CTkLabel(self, text="Account Name:")
        self.name_label.pack()
        self.name_entry = ctk.CTkEntry(self, width=200)
        self.name_entry.pack(pady=5)

        # Initial Balance Entry
        self.balance_label = ctk.CTkLabel(self, text="Initial Balance:")
        self.balance_label.pack()
        self.balance_entry = ctk.CTkEntry(self, width=200)
        self.balance_entry.pack(pady=5)

        # Create Account Button
        self.create_button = ctk.CTkButton(self, text="Create Account", command=self.create_account)
        self.create_button.pack(pady=10)

        # Deposit Entry
        self.deposit_label = ctk.CTkLabel(self, text="Deposit Amount:")
        self.deposit_label.pack()
        self.deposit_entry = ctk.CTkEntry(self, width=200)
        self.deposit_entry.pack(pady=5)

        # Deposit Button
        self.deposit_button = ctk.CTkButton(self, text="Deposit", command=self.deposit)
        self.deposit_button.pack(pady=10)

        # Withdraw Entry
        self.withdraw_label = ctk.CTkLabel(self, text="Withdraw Amount:")
        self.withdraw_label.pack()
        self.withdraw_entry = ctk.CTkEntry(self, width=200)
        self.withdraw_entry.pack(pady=5)

        # Withdraw Button
        self.withdraw_button = ctk.CTkButton(self, text="Withdraw", command=self.withdraw)
        self.withdraw_button.pack(pady=10)

        # Check Balance Button
        self.balance_button = ctk.CTkButton(self, text="Check Balance", command=self.show_balance)
        self.balance_button.pack(pady=10)

        # Print Statement Button
        self.statement_button = ctk.CTkButton(self, text="Print Statement", command=self.show_statement)
        self.statement_button.pack(pady=10)

    def create_account(self):
        """Creates a new account."""
        name = self.name_entry.get()
        initial_balance = self.balance_entry.get()
        try:
            initial_balance = float(initial_balance)
            self.account = Account(name, initial_balance)
            messagebox.showinfo("Success", f"Account created for {name} with initial balance ${initial_balance:.2f}.")
        except ValueError:
            messagebox.showerror("Error", "Initial balance must be a number.")
        except InvalidAmountError as e:
            messagebox.showerror("Error", str(e))

    def deposit(self):
        """Deposits money into the account."""
        if not self.account:
            messagebox.showerror("Error", "No account found. Please create an account first.")
            return

        amount = self.deposit_entry.get()
        try:
            amount = float(amount)
            self.account.deposit(amount)
            messagebox.showinfo("Success", f"Deposited ${amount:.2f}. New balance: ${self.account.balance:.2f}.")
        except ValueError:
            messagebox.showerror("Error", "Deposit amount must be a number.")
        except InvalidAmountError as e:
            messagebox.showerror("Error", str(e))

    def withdraw(self):
        """Withdraws money from the account."""
        if not self.account:
            messagebox.showerror("Error", "No account found. Please create an account first.")
            return

        amount = self.withdraw_entry.get()
        try:
            amount = float(amount)
            self.account.withdraw(amount)
            messagebox.showinfo("Success", f"Withdrew ${amount:.2f}. New balance: ${self.account.balance:.2f}.")
        except ValueError:
            messagebox.showerror("Error", "Withdrawal amount must be a number.")
        except (InvalidAmountError, InsufficientBalanceError) as e:
            messagebox.showerror("Error", str(e))

    def show_balance(self):
        """Displays the current balance."""
        if not self.account:
            messagebox.showerror("Error", "No account found. Please create an account first.")
            return

        balance = self.account.check_balance()
        messagebox.showinfo("Balance", f"Current balance: ${balance:.2f}.")

    def show_statement(self):
        """Displays the transaction statement."""
        if not self.account:
            messagebox.showerror("Error", "No account found. Please create an account first.")
            return

        statement = self.account.print_statement()
        messagebox.showinfo("Transaction Statement", statement)

# Run the Application
if __name__ == "__main__":
    app = BankingApp()
    app.mainloop()