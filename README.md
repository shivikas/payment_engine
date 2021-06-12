# Payment Engine
Dummy payment engine that reads a series of transactions from a CSV, updates client accounts,
handles disputes and chargebacks, and then outputs the state of clients accounts as a CSV.

## Packages to install
pip install -r requirements.txt

## Run program
Clone the repo and from CLI execute following command to run the engine.

> python engine.py transactions.csv > accounts.csv

Input file: transactions.csv

Please replace this file to run application on different input data set. Keep the file name same.


Output file: accounts.csv

Out put is generated on the stdout. In the command above it is redirected to accounts.csv file.


## PyTest
Unit tests are written using python pytest module.
Tests are available in folder /test
To run pytest in verbose mode, execute following command form
inside the repo folder from command line.

> pytest -vs  test/app_test.py


## Assumptions
I have made some assumptions during the implementation.
I have tried to capture them in the doc string in the modules.

Some of them are:
1. Create client if do not exist already.
2. Only deposit transactions can be disputed.
3. Transactions referred by disputed or resolved or chargeback transactions
 are searched in the transactions set above disputed, resolved or chargeback transactions.
 

