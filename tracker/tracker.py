import requests
import json


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
        exit()


def patch_peers(peers, my_address):
    path = api_path + data_path
    data = {
        "fields": {
            "list": {
                "arrayValue": {
                    "values": []
                }
            }
        }
    }
    for peer in peers:
        data['fields']['list']['arrayValue']['values'].append({'stringValue': peer})
    data['fields']['list']['arrayValue']['values'].append({'stringValue': my_address})
    # print(json.dumps(data))
    response = requests.patch(path, json.dumps(data))
    if response.ok:
        print('Updated peer list in tracker')
    else:
        print('Failed to update peer list in tracker')
    return response.ok
