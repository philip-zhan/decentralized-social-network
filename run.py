import subprocess
import requests
import server

api_path = 'https://firestore.googleapis.com/v1beta1/'
data_path = 'projects/dsn-tracker/databases/(default)/documents/peer/address'
path = api_path + data_path
response = requests.get(path)
if response.ok:
    peers = response.json()['fields']['list']['arrayValue']['values']
    peers = [peer['stringValue'] for peer in peers]
    server.main(peers)
else:
    print("Failed to access tracker at ", path)
