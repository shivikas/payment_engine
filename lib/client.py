"""Client module."""

from decimal import *

getcontext().prec = 4


class Client:
    """Class to hold client related data."""
    def __init__(self, client_id):
        """Initialize the client object."""
        self.client_id = client_id
        self.available_balance = Decimal()
        self.held_amount = Decimal()
        self.total_amount = Decimal()
        self.disputed_transactions = set()
        self.locked = False

    def deposite_on_account(self, amount):
        """Deposite on clients account.

        Args:
            amount (float): Credit to clients account.

        """
        if not self.locked:
            self.available_balance += Decimal(str(amount))
            self.total_amount += Decimal(str(amount))

    def withdraw_on_account(self, amount):
        """Withdraw from the client’s asset account.

        Args:
            amount (float): Debit from clients account.

        """
        if self.available_balance >= Decimal(str(amount))\
                and not self.locked:
            self.available_balance -= Decimal(str(amount))
            self.total_amount -= Decimal(str(amount))

    def dispute_on_account(self, amount, tx_id):
        """Client claim that a transaction was erroneous and should be reverse.

        Transaction shouldn’t be reversed yet but the associated funds should be held.
        This means that the clients available funds should decrease by the amount disputed,
        their held funds should increase by the amount disputed while their total funds
        should remain the same.

        Args:
            amount (float): Debit from clients account.
            tx_id (uint32): Unique transaction ID

        """
        if self.available_balance >= Decimal(str(amount)) \
                and not self.locked:
            self.available_balance -= Decimal(str(amount))
            self.held_amount += Decimal(str(amount))
            self.disputed_transactions.add(tx_id)

    def resolve_on_account(self, amount, tx_id):
        """Resolve represents a resolution to a dispute.

        It Releases the associated held funds.
        Funds that were previously disputed are no longer disputed.
        The clients held funds should decrease by the amount no longer disputed.
        Their available funds should increase by the amount no longer disputed,
        and their total funds should remain the same.

        Args:
            amount (float): Debit from clients account.
            tx_id (uint32): Unique transaction ID

        """
        if tx_id in self.disputed_transactions and not self.locked:
            self.held_amount -= Decimal(amount)
            self.available_balance += Decimal(amount)
            self.disputed_transactions.remove(tx_id)

    def chargeback_on_account(self, amount, tx_id):
        """Chargeback is the final state of a dispute.

        It represents the client reversing a transaction.
        Held funds have now been withdrawn. The clients held funds and
        total funds should decrease by the amount previously disputed.
        If a chargeback occurs the client’s account should be immediately
        frozen.

        Args:
            amount (float): Debit from clients account.
            tx_id (uint32): Unique transaction ID

        """
        if tx_id in self.disputed_transactions and not self.locked:
            self.held_amount -= Decimal(amount)
            self.total_amount -= Decimal(amount)
            self.locked = True
