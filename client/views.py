import datetime
import json
import requests
from flask import render_template, redirect, request, send_from_directory
from client import app


CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"
posts = []


def fetch_posts():
    get_chain_address = "{}/sync".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.ok:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'], reverse=True)


@app.route('/')
def index():
    mine_request = "{}/mine".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(mine_request)
    if response.ok:
        print(response)
    fetch_posts()
    return render_template('index.html',
                           title='Mask',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    post_content = request.form["content"]
    author = request.form["author"]

    post_object = {
        'author': author,
        'content': post_content,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')

# @app.route('/fonts/<path:filename>')
# def serve_static(filename):
#     root_dir = os.path.dirname(os.getcwd())
#     return send_from_directory(os.path.join(root_dir, 'static', 'ttf'),

def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
