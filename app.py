from flask import Flask
from hashlib import sha256
import json

app = Flask(__name__)

class Block(object):
	"""docstring for Block"""
	def __init__(self, index, transactions, timestamp):
		super(Block, self).__init__()
		self.index = index
		self.transactions = transactions
		self.timestamp = timestamp

	def compute_hash(block):
		block_string = json.dumps(self.__dict__, sort_keys=True)
		return sha256(block_string.encode()).hexdigest()

		



@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
