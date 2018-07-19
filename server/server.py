from flask import Flask, request, jsonify
import requests
import json
import time
from server.Blockchain import Blockchain
from server.Block import Block
import tracker


app = Flask(__name__)
# the node's copy of blockchain
blockchain = Blockchain()
# the address to other participating members of the network
peers = set()
my_address = ''


def main(_my_address, _peers):
    global peers, my_address
    peers = set(_peers)
    my_address = _my_address
    if my_address in peers:
        peers.remove(my_address)
    else:
        tracker.patch_peers(peers, my_address)
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


def consensus():
    """
    Our simple consensus algorithm. If a longer valid chain is found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for peer in peers:
        print("syncing with peer:", peer)
        print("=======================================================")
        try:
            response = requests.get(peer + '/chain', timeout=1)
        except:
            print("connection timeout")
            continue
        if response.ok:
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
        print(longest_chain)
        return True

    return False


if __name__ == '__main__':
    main()
