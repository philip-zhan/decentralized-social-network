import requests


api_path = 'https://firestore.googleapis.com/v1beta1/'
data_path = 'projects/dsn-tracker/databases/(default)/documents/peer/address'


def get_peers():
    path = api_path + data_path
    response = requests.get(path)
    if response.ok:
        peers = response.json()['fields']['list']['arrayValue']['values']
        peers = [peer['stringValue'] for peer in peers]
        print('Found peers:', peers)
        return peers
        # './ngrok http 8000'
        # ngrok = subprocess.Popen('./ngrok http 8000')
        # subprocess.Popen('python3 client.py', shell=True)
        # server.main(peers)
        # subprocess.run(['python3 client.py'], shell=True)
    else:
        print("Failed to access tracker at ", path)


def patch_peers():
    pass
