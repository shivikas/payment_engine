"""Module to process input cvs file."""

import sys
import csv
import numpy as np
import pandas as pd

from lib.client import Client


class PaymentEngine:
    """Payment engine class."""

    def __init__(self, infile):
        """Instantiate payment engine."""
        self.infile = infile
        self.transactions_df = pd.read_csv(self.infile,)
        self._header = ["client", "available", "held", "total", "locked"]
        self.outfile_writer = None
        self.clients = {}
        self.tx_array = self.transactions_df[["tx"]].to_numpy(dtype=np.uint32)

    def process_clients_transactions_data(self):
        """Read and process clients transactions data."""
        try:
            for idx, tx_data in self.transactions_df.iterrows():
                if tx_data["type"] == "deposit":
                    if not self.__client_exist(tx_data["client"]):
                        self.__create_client(tx_data["client"])
                    self.__call_deposit(tx_data)

                if tx_data["type"] == "withdraw" or tx_data["type"] == "withdrawal":
                    self.__call_withdraw(tx_data)

                if tx_data["type"] == "dispute":
                    self.__call_dispute(idx, tx_data)

                if tx_data["type"] == "resolve":
                    self.__call_resolve(idx, tx_data)

                if tx_data["type"] == "chargeback":
                    self.__call_chargeback(idx, tx_data)
        except Exception as e:
            print(f"Following exception has occurred: {e}")

    def __create_client(self, client_id):
        """Create client if not exist.

        Args:
            client_id (int): Client ID

        """
        self.clients[client_id] = Client(client_id)

    def __client_exist(self, client_id):
        """Check if client exist.

        Args:
            client_id (int): Client ID.

        Returns:
            bool: Returns True if client exists else False.

        """
        if client_id in self.clients:
            return True
        return False

    def __call_deposit(self, tx_data):
        """Deposit is a credit to the client’s asset account.

        It should increase the available and total funds of the
        client account.

        Args:
            tx_data (data frame): Client's transaction data.

        """
        client, amount = tx_data["client"], tx_data["amount"]
        client_data = self.clients[client]
        client_data.deposite_on_account(amount)

    def __call_withdraw(self, tx_data):
        """Withdraw is a debit to the client’s asset account.

        It should decrease the available and total funds of the
        client account

        Args:
            tx_data (data frame): Client's transaction data.

        """
        client, amount = tx_data["client"], tx_data["amount"]
        client_data = self.clients[client]
        client_data.withdraw_on_account(amount)

    def __call_dispute(self, idx, tx_data):
        """Dispute is client’s claim that a transaction was erroneous and should be reverse.

        Dispute does not state the amount disputed.
        It references the transaction that is disputed by ID.
        If the tx specified by the dispute doesn’t exist
        you can ignore it.

        (NOTE: I am assuming the transaction type disputed will be "deposit")

        Args:
            idx : Index in pandas data frame.
            tx_data (data frame): Client's transaction data.

        """
        row, col = np.where(self.tx_array[:idx] == tx_data["tx"])
        if len(row) > 0:
            client_tx_data = self.transactions_df.iloc[row[0]]
            if tx_data["client"] == client_tx_data["client"]\
                and self.__client_exist(tx_data["client"])\
                    and client_tx_data["type"] == "deposit":
                client_data = self.clients[tx_data["client"]]
                client_data.dispute_on_account(client_tx_data["amount"],
                                               client_tx_data["tx"])

    def __call_resolve(self, idx, tx_data):
        """Resolve represents a resolution to a dispute.

        Resolve does not specify an amount.
        Instead it refers to a transaction that was under dispute by ID
        If the transaction specified doesn’t exist, or the transaction isn’t
        under dispute, ignore the resolve.

        Args:
            idx : Index in pandas data frame.
            tx_data (data frame): Client's transaction data.

        """
        row, col = np.where(self.tx_array[:idx] == tx_data["tx"])
        if len(row) > 0:
            client_tx_data = self.transactions_df.iloc[row[0]]
            if tx_data["client"] == client_tx_data["client"] \
                    and self.__client_exist(tx_data["client"]) \
                    and client_tx_data["type"] == "deposit":
                client_data = self.clients[tx_data["client"]]
                client_data.resolve_on_account(client_tx_data["amount"],
                                               client_tx_data["tx"])

    def __call_chargeback(self, idx, tx_data):
        """Chargeback represents the client reversing a transaction.

        Chargeback refers to the transaction by transaction id and
        does not specify an amount.
        If the transaction specified doesn’t exist, or the transaction isn’t
        under dispute, ignore chargeback.

        Args:
            idx : Index in pandas data frame.
            tx_data (data frame): Client's transaction data.

        """
        row, col = np.where(self.tx_array[:idx] == tx_data["tx"])
        if len(row) > 0:
            client_tx_data = self.transactions_df.iloc[row[0]]
            if tx_data["client"] == client_tx_data["client"] \
                    and self.__client_exist(tx_data["client"]) \
                    and client_tx_data["type"] == "deposit":
                client_data = self.clients[tx_data["client"]]
                client_data.chargeback_on_account(client_tx_data["amount"],
                                                  client_tx_data["tx"])

    def generate_results(self):
        self.outfile_writer = csv.DictWriter(sys.stdout, self._header)
        self.outfile_writer.writeheader()
        for _, client in self.clients.items():
            self.outfile_writer.writerow({
                "client": client.client_id,
                "available": client.available_balance,
                "held": client.held_amount,
                "total": client.total_amount,
                "locked": client.locked
            })
