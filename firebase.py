import requests


api_path = 'https://firestore.googleapis.com/v1beta1/'
data_path = 'projects/dsn-tracker/databases/(default)/documents/peer/address'
key = ''
response = requests.get(api_path + data_path)

print(response.json())
