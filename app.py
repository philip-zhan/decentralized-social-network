from flask import Flask
from hashlib import sha256
import json
import time

class Block(object):
	def __init__(self, index, transactions, timestamp, previous_hash):
		super(Block, self).__init__()
		self.index = index
		self.transactions = transactions
		self.timestamp = timestamp
		self.previous_hash = previous_hash

	def compute_hash(self):
		block_string = json.dumps(self.__dict__, sort_keys=True)
		return sha256(block_string.encode()).hexdigest()

class Blockchain(object):
	difficulty = 2

	def __init__(self):
		super(Blockchain, self).__init__()
		self.unconfirmed_transactions = []
		self.chain = []
		self.create_genesis_block()

	def create_genesis_block(self):
		genesis_block = Block(0,[],time.time(),"0")
		genesis_block.hash = genesis_block.compute_hash()
		self.chain.append(genesis_block)

	@property
	def last_block(self):
		return self.chain[-1]

	def proof_of_work(self, block):
		# generate hash according to given difficulty
		block.nonce = 0
		computed_hash = block.compute_hash()
		while not computed_hash.startswith(0*Blockchain.difficulty):
			block.nonce += 1
			computed_hash = block.compute_hash
		return computed_hash

	def is_valid_proof(self, block, block_hash):
		return (block_hash.startswith(0*Blockchain.difficulty) and block_hash == block.compute_hash)

	def add_block(self, block, proof):
		# verify if proof is correct
		# verify if the last transaction's hash provided by this block is correct
		previous_hash = self.last_block.hash
		if previous_hash != block.previous_hash:
			return False
		if not self.is_valid_proof(block, proof):
			return False
		# add block
		block.hash = proof
		self.chain.append(block)

	def add_new_transaction(self, transaction):
		self.unconfirmed_transactions.append(transaction)

	def mine():
		# add pending transactions to a block,
		# compute proof of work for block,
		# add block to blockchain
		if not self.unconfirmed_transactions:
			return False

		last_block = self.last_block
		new_block = Block(index=last_block.index+1,
							transactions = self.unconfirmed_transactions,
							timestamp = time.time(),
							previous_hash = last_block.hash)
		proof = self.proof_of_work(new_block)
		self.add_block(new_block, proof)

		self.unconfirmed_transactions = []
		return new_block

app = Flask(__name__)

blockchain = Blockchain()

@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["author", "content"]
 
    for field in required_fields:
        if not tx_data.get(field):
            return "Invlaid transaction data", 404
 
    tx_data["timestamp"] = time.time()
 
    blockchain.add_new_transaction(tx_data)
 
    return "Success", 201

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})

@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    return "Block #{} is mined.".format(result)
 
 
# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)

# @app.route('/')
# def hello_world():
#     return 'Hello World!'


if __name__ == '__main__':
    app.run()
