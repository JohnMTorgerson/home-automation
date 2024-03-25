import requests

def request(dir):
    # eventually we'll need a list of different servers to send the request to

    url = 'http://192.168.2.200:5000/run_shades'
    data = { "dir": dir }

    r = requests.post(url=url, json=data)

    return r.text
