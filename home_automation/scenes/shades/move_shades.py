import requests
# import sys
# import os
# sys.path.insert(1, os.path.abspath('/home/pi/Projects/ha-auto-shades'))
# import auto_shades

url = 'http://192.168.2.200:5000/run_shades'

def request(dir):
    # eventually we'll need a list of different servers to send the request to

    data = { "dir": dir }

    r = requests.post(url=url, json=data)
    r.raise_for_status() # raise an exception unless status is 200

    return r.text

#def request(dir):
#    auto_shades.run(dir)
#    return "Success"

# import aiohttp
# import asyncio

# async def request(dir):

#     data = { "dir": dir }

#     async with aiohttp.ClientSession(raise_for_status=True) as session:
#         async with session.request('post',url,json=data) as response:

#             print("Status:", response.status)
#             print("Content-type:", response.headers['content-type'])

#             return await response.text()
