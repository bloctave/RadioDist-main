from dotenv import load_dotenv
load_dotenv()  # This loads the environment variables from a .env file
import os
import psycopg2
import json
from web3 import Web3

# Environment variables
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_PORT = os.getenv('DATABASE_PORT', 5432)
INFURA_URL = os.getenv('INFURA_URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
CONTRACT_ABI = json.loads(os.getenv('CONTRACT_ABI'))

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(INFURA_URL))
account = web3.eth.account.from_key(PRIVATE_KEY)

def get_distribution_amount():
    try:
        with psycopg2.connect(
            host=DATABASE_HOST,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            port=DATABASE_PORT
        ) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT "Wallet Address", "Total to be Distributed" FROM "Daily_Table" ORDER BY "Artist" ASC LIMIT 1')
                row = cur.fetchone()
                if row:
                    print(f"Fetched row: {row}")  # Debugging line
                    return row[0], float(row[1])
                return None, 0
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise

def send_update_amount(recipient, amount):
    contract = web3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=CONTRACT_ABI)
    
    # Convert amount to integer based on token's decimals
    DECIMAL_FACTOR = 10**6  # Assuming USDT with 6 decimals
    amount_in_wei = int(amount * DECIMAL_FACTOR)
    
    # Ensure recipient address is checksummed
    checksum_recipient = Web3.to_checksum_address(recipient)
    
    # Print the amount and wallet address
    print(f"Sending {amount} to wallet address {checksum_recipient}")
    
    # Debugging: Print the contract function object
    distribute_function = contract.functions.distribute(checksum_recipient, amount_in_wei)
    print(f"Distribute function: {distribute_function}")
    print(f"Distribute function attributes: {dir(distribute_function)}")
    print(contract)
    print(distribute_function)
    
# Reference to the function
distribute_function = contract.functions.distribute

# Build the transaction with the function reference
transaction = distribute_function(checksum_recipient, amount_in_wei).buildTransaction({
    'from': account.address,
    'chainId': 137,  # Polygon Mainnet
    'gas': 2000000,
    'gasPrice': web3.toWei('30', 'gwei'),
    'nonce': web3.eth.getTransactionCount(account.address),
})

# Sign and send the transaction
signed_txn = web3.eth.account.signTransaction(transaction, private_key=PRIVATE_KEY)
tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
print(f"Transaction hash: {tx_hash.hex()}")

def main():
    try:
        recipient, amount = get_distribution_amount()
        if recipient is None:
            print(json.dumps({'message': 'No distributions to process'}))
            return

        tx_hash = send_update_amount(recipient, amount)
        print(json.dumps({'transaction_hash': tx_hash}))
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    main()