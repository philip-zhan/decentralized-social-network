import subprocess
import requests
import tracker
import server
import client


def main():
    my_address = run_ngrok()
    peers = tracker.get_peers()
    run_server(my_address, peers)


def run_ngrok():
    subprocess.Popen(['./ngrok', 'http', '8000'], stdout=subprocess.PIPE)
    response = requests.get('http://localhost:4040/api/tunnels')
    if response.ok and len(response.json()['tunnels']) > 0:
        tunnels = response.json()['tunnels']
        for tunnel in tunnels:
            if tunnel['proto'] == 'http' and tunnel['config']['addr'] == 'localhost:8000':
                public_url = tunnel['public_url']
                print('Public URL:', public_url)
                return public_url
    print('Failed to start ngrok')
    exit()


def run_server(my_address, peers):
    server.main(my_address, peers)


if __name__ == '__main__':
    main()
