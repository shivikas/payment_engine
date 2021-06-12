"""
This module describes simple payments engine that:
 1. Reads a series of transactions from an input CSV file.
 2. Updates client accounts.
 3. Handles disputes and chargebacks.
4. Then finally outputs the state of clients accounts as an output CSV file.

To run the program, run following command from CLI:
>   python engine.py transactions.csv > accounts.csv
where:
transactions.csv: is the required input argument to the engine.py.
accounts.csv: is the output file, where results will be writen in.

"""

import argparse
from pathlib import Path

from lib.payment_engine import PaymentEngine


def main():
    parser = argparse.ArgumentParser(prog="engine.py", description="Simple payment engine.")
    parser.add_argument("input_file", default="transactions.csv", type=Path,
                        help=" the input file to %(prog)s (default: %(default)s)")
    args = parser.parse_args()

    if not args.input_file.is_file():
        raise FileNotFoundError
    payment_engine = PaymentEngine(args.input_file)
    payment_engine.process_clients_transactions_data()
    payment_engine.generate_results()


if __name__ == "__main__":
    main()
