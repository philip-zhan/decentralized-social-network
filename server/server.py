import requests
import json
import time
import pickle
import os
from flask import Flask, request, jsonify
from server.Blockchain import Blockchain
from server.Block import Block
from pathlib import Path
from tracker import tracker


app = Flask(__name__)
# the node's copy of blockchain
blockchain = Blockchain()
# the address to other participating members of the network
peers = set()
my_address = ''
cache_path = '.cache'
blockchain_cache_path = cache_path + '/blockchain'


def main(_my_address):
    global my_address, blockchain
    my_address = _my_address
    create_cache_dir(cache_path)
    blockchain = get_update_local_chain(blockchain)
    # print("Chain on startup is: {}".format(blockchain.chain))
    # print("Got local chain on startup: {}".format(blockchain.chain))
    app.run(port=8000, debug=True)


# endpoint to add new peers to the network.
@app.route('/add_nodes', methods=['POST'])
def register_new_peers():
    nodes = request.get_json()
    if not nodes:
        return "Invalid data", 400
    for node in nodes:
        peers.add(node)

    return "Success", 201


# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
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


# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def get_chain():
    # make sure we've the longest chain
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return jsonify({"length": len(chain_data), "chain": chain_data})


# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    announce_new_block(blockchain.last_block)
    return "Block #{} is mined.".format(result)


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return jsonify(blockchain.unconfirmed_transactions)


# endpoint to add a block mined by someone else to the node's chain.
@app.route('/add_block', methods=['POST'])
def validate_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"], block_data["transactions"],
                  block_data["timestamp", block_data["previous_hash"]])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


# endpoint to sync the blockchain and return the new blockchain
@app.route('/sync', methods=['GET'])
def sync():
    consensus()
    sync_chain = get_chain()

    return sync_chain, 200


def announce_new_block(block):
    for peer in peers:
        url = "http://{}/add_block".format(peer)
        try:
            requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))
        except:
            # Delete the server that is down
            print("peer {} is down".format(str(peer)))


def create_cache_dir(cache_path):
    cache_dir = Path(cache_path)
    if not cache_dir.is_dir():
        os.mkdir(cache_path)


# get the chain stored locally or update the stored blockchain
def get_update_local_chain(blockchain):
    blockchain_file = Path(blockchain_cache_path)
    longest_chain = blockchain
    # Get the local blockchain if it exist
    if blockchain_file.is_file():
        with open(blockchain_cache_path, 'rb') as f:
            local_blockchain = pickle.load(f)
        print("local chain loaded: {} with length {}".format(local_blockchain, len(local_blockchain.chain)))

        if len(local_blockchain.chain) < len(blockchain.chain):
            longest_chain = blockchain
            print("Global chain is the longest one and it is saved")
            # save to the local chain
            with open(blockchain_cache_path, 'wb') as f:
                pickle.dump(longest_chain, f)
        else:
            longest_chain = local_blockchain
            print("local chain is longest chain with length: {}".format(len(longest_chain.chain)))
    else:
        print("No local chain, new chain is stored. returned: {}".format(blockchain))
        # save to the local chain
        with open(blockchain_cache_path, 'wb') as f:
            pickle.dump(blockchain, f)

    return longest_chain


def consensus():
    """
    Our simple consensus algorithm. If a longer valid chain is found, our chain is replaced with it.
    """
    global blockchain, peers

    longest_chain = None
    current_len = len(blockchain.chain)
    peers = tracker.get_peers(my_address)

    for peer in peers:
        try:
            response = requests.get(peer + '/chain', timeout=0.5)
        except:
            print('Failed to sync with peer', peer)
            continue
        if response.ok:
            print('Synced with peer', peer)
            length = response.json()['length']
            chain = response.json()['chain']
            # print(chain)
            # print(length)
            # print("current length: ", current_len)
            if length > current_len and blockchain.check_chain_validity(chain):
                # print("longer chain")
                current_len = length
                longest_chain = chain

    if longest_chain:
        blockchain = Blockchain(longest_chain)
        print("COPIED THE LONGEST CHAIN")
        #print(longest_chain)
        get_update_local_chain(blockchain)
        return True

    return False


if __name__ == '__main__':
    main()
