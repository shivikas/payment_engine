"""Testing application with sample data sets."""

import pytest
from decimal import *
from io import StringIO

from lib.payment_engine import PaymentEngine

getcontext().prec = 4


def test_correct_transactions():
    """Test with correct transactions
    Verify available balance for client1 and client2.
    """
    in_mem_csv = StringIO(
        "type,client,tx,amount\n"
        "deposit,1,1,1.0\n"
        "deposit,2,2,2.0\n"
        "deposit,1,3,2.0\n"
        "withdrawal,1,4,1.5\n"
        "withdrawal,2,5,1.5\n"
    )
    app = PaymentEngine(in_mem_csv)
    app.process_clients_transactions_data()
    client1 = app.clients[1]
    client2 = app.clients[2]
    assert client1.available_balance == Decimal(1.5)
    assert client2.available_balance == Decimal(0.5)


def test_tx_with_dispute():
    """Test when disputed transaction exist for a client."""
    in_mem_csv = StringIO(
        "type,client,tx,amount\n"
        "deposit,1,1,1.0\n"
        "deposit,1,2,2.0\n"
        "withdrawal,1,3,1.0\n"
        "dispute,1,2\n"
    )
    app = PaymentEngine(in_mem_csv)
    app.process_clients_transactions_data()
    client1 = app.clients[1]
    assert client1.available_balance == Decimal(0.0)
    assert client1.held_amount == Decimal(2.0)
    assert client1.total_amount == Decimal(2.0)


def test_tx_with_dispute_but_insufficient_available_balance():
    """Test when disputed transaction exist for a client.
    But the available funds are less than disputed amount.
    """
    in_mem_csv = StringIO(
        "type,client,tx,amount\n"
        "deposit,1,1,1.0\n"
        "deposit,1,2,2.0\n"
        "withdrawal,1,3,3.0\n"
        "dispute,1,2\n"
    )
    app = PaymentEngine(in_mem_csv)
    app.process_clients_transactions_data()
    client1 = app.clients[1]
    assert client1.available_balance == Decimal(0.0)
    assert client1.held_amount == Decimal(0.0)


def test_tx_with_dispute_and_resolve():
    """Test when disputed transaction exist for a client and resolved."""
    in_mem_csv = StringIO(
        "type,client,tx,amount\n"
        "deposit,1,1,1.0\n"
        "deposit,1,2,2.0\n"
        "dispute,1,2\n"
        "resolve,1,2"
    )
    app = PaymentEngine(in_mem_csv)
    app.process_clients_transactions_data()
    client1 = app.clients[1]
    assert client1.available_balance == Decimal(3.0)
    assert client1.held_amount == Decimal(0.0)


def test_tx_with_chargeback():
    """Test when chargeback occures."""
    in_mem_csv = StringIO(
        "type,client,tx,amount\n"
        "deposit,1,1,1.0\n"
        "deposit,1,2,2.0\n"
        "dispute,1,2\n"
        "chargeback,1,2"
    )
    app = PaymentEngine(in_mem_csv)
    app.process_clients_transactions_data()
    client1 = app.clients[1]
    assert client1.available_balance == Decimal(1.0)
    assert client1.held_amount == Decimal(0.0)
    assert client1.total_amount == Decimal(1.0)
    assert client1.locked is True


def test_tx_chargeback_with_insufficient_held_funds():
    """Test when chargeback occures, and held amount is not sufficient.
    Note: chargeback back transaction is not in dispute.
    """
    in_mem_csv = StringIO(
        "type,client,tx,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "dispute,1,2\n"
        "chargeback,1,1"
    )
    app = PaymentEngine(in_mem_csv)
    app.process_clients_transactions_data()
    client1 = app.clients[1]
    assert client1.available_balance == Decimal(3.0)
    assert client1.held_amount == Decimal(2.0)
    assert client1.total_amount == Decimal(5.0)
    assert client1.locked is False


def test_tx_with_deposit_after_chargeback():
    """Test when client deposit on locked account."""
    in_mem_csv = StringIO(
        "type,client,tx,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "dispute,1,1\n"
        "chargeback,1,1\n"
        "deposit,1,1,11.0\n"
    )
    app = PaymentEngine(in_mem_csv)
    app.process_clients_transactions_data()
    client1 = app.clients[1]
    assert client1.available_balance == Decimal(2.0)
    assert client1.held_amount == Decimal(0.0)
    assert client1.total_amount == Decimal(2.0)
    assert client1.locked is True


def test_tx_with_witdraw_after_chargeback():
    """Test when client try to withdraw on locked account."""
    in_mem_csv = StringIO(
        "type,client,tx,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "dispute,1,1\n"
        "chargeback,1,1\n"
        "withdrawal,1,1,1.5\n"
    )
    app = PaymentEngine(in_mem_csv)
    app.process_clients_transactions_data()
    client1 = app.clients[1]
    assert client1.available_balance == Decimal(2.0)
    assert client1.held_amount == Decimal(0.0)
    assert client1.total_amount == Decimal(2.0)
    assert client1.locked is True


def test_tx_with_dispute_on_withdraw():
    """Test when dispute refers to withdraw transaction."""
    in_mem_csv = StringIO(
        "type,client,tx,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "withdrawal,1,3,1.5\n"
        "dispute,1,3\n"
    )
    app = PaymentEngine(in_mem_csv)
    app.process_clients_transactions_data()
    client1 = app.clients[1]
    assert client1.available_balance == Decimal(3.5)
    assert client1.held_amount == Decimal(0.0)
    assert client1.total_amount == Decimal(3.5)
    assert client1.locked is False


def test_when_referred_dispute_tx_not_exist():
    """Test when the referred tx by dispute do not exist."""
    in_mem_csv = StringIO(
        "type,client,tx,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "withdrawal,1,3,1.5\n"
        "dispute,1,4\n"
    )
    app = PaymentEngine(in_mem_csv)
    app.process_clients_transactions_data()
    client1 = app.clients[1]
    assert client1.available_balance == Decimal(3.5)
    assert client1.held_amount == Decimal(0.0)
    assert client1.total_amount == Decimal(3.5)
    assert client1.locked is False


def test_when_referred_resolve_tx_not_exist():
    """Test when tx referred by resolve do not exist."""
    in_mem_csv = StringIO(
        "type,client,tx,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "dispute,1,2\n"
        "resolve,1,4\n"
    )
    app = PaymentEngine(in_mem_csv)
    app.process_clients_transactions_data()
    client1 = app.clients[1]
    assert client1.available_balance == Decimal(3.0)
    assert client1.held_amount == Decimal(2.0)
    assert client1.total_amount == Decimal(5.0)
    assert client1.locked is False


def test_when_dispute_client_do_not_match():
    """Test when client on dispute transaction do not match
    the client on referred transaction and resolved is called.
    """
    in_mem_csv = StringIO(
        "type,client,tx,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "dispute,2,2\n"
        "resolve,1,2\n"
    )
    app = PaymentEngine(in_mem_csv)
    app.process_clients_transactions_data()
    client1 = app.clients[1]
    assert client1.available_balance == Decimal(5.0)
    assert client1.held_amount == Decimal(0.0)
    assert client1.total_amount == Decimal(5.0)
    assert client1.locked is False


def test_when_resolve_client_do_not_match():
    """Test when client on resolve transaction do not
    match the client on refered trandaction.
    """
    in_mem_csv = StringIO(
        "type,client,tx,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "dispute,1,2\n"
        "resolve,2,2\n"
    )
    app = PaymentEngine(in_mem_csv)
    app.process_clients_transactions_data()
    client1 = app.clients[1]
    assert client1.available_balance == Decimal(3.0)
    assert client1.held_amount == Decimal(2.0)
    assert client1.total_amount == Decimal(5.0)
    assert client1.locked is False


def test_transaction_with_decimal_precision():
    """Test transactions with decimal precision of four."""
    in_mem_csv = StringIO(
        "type,client,tx,amount\n"
        "deposit,1,1,3.1239\n"
        "deposit,1,2,2.1239\n"
    )
    app = PaymentEngine(in_mem_csv)
    app.process_clients_transactions_data()
    client1 = app.clients[1]
    assert client1.available_balance == Decimal(3.1239) + Decimal(2.1239)
    assert client1.total_amount == Decimal(3.1239) + Decimal(2.1239)
