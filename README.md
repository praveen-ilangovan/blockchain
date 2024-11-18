# Blockchain

### A basic blockchain project written in Python using cryptography module.

### Usage

Setting up python2.7 and virtual environment in windows using pyenv

```sh
cd blockchain
pyenv install 2.7.18
pyenv local 2.7.18
set PYTHONIOENCODING=UTF-8 # To avoid LookupError: unknown encoding: cp65001
python -m pip install virtualenv
```

Installing the requirments

```sh
python -m virtualenv .venv
.venv/Scripts/activate.bat
python -m pip install -r requirements.txt
python
```

#### Example snippet
```python
import blockchain

# Create a few wallets
user1 = blockchain.generate_wallet("User1", "User1Password")
user2 = blockchain.generate_wallet("User2", "User2Password")
user3 = blockchain.generate_wallet("User3", "User3Password")

# Make a few transactions
blockchain.submit_transaction('User1', 'User2', 2.0, "User1Password")
blockchain.submit_transaction('User2', 'User3', 1.5, "User2Password")
blockchain.submit_transaction('User3', 'User1', 2.55, "User3Password")
blockchain.submit_transaction('User2', 'User1', 2.01, "User2Password")

# Add them to the blockchain
blockchain.mine()

```

#### Running test
```sh
cd blockchain
python -m pytest
```
