import requests

# eventually we'll need a list of different server urls to send the request to
url = 'http://192.168.2.200:5000/run_shades'

def request(dir):

    data = { "dir": dir }

    r = requests.post(url=url, json=data)
    r.raise_for_status() # raise an exception unless status is 200

    return r.text
