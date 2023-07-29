import os
from pprint import pprint

# # use the following when testing wyze_sdk from local fork
# import sys
# # insert at 1: 0 is the script path (or '' in REPL)
# sys.path.insert(1, os.path.abspath('../../!...Forks/'))

from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError

import login

client = login.get_client()

def main() :
    # get_devices()
    test_graphics()

def test_graphics() :
    from scenes.timebased.sunlight import sunlight_graphics as sg
    sg.open()


def get_devices() :
    try:
        devices = client.devices_list()
        # bulbs = get_devices.get_by_type(client,'MeshLight')
        for device in devices:
            # print(f"mac: {device.mac}")
            print(f"nickname: {device.nickname}")
            # print(f"is_online: {device.is_online}")
            # print(f"product model: {device.product.model}")
            # pprint(device)

            if device.type == 'MeshLight' :
                test_bulb(device.mac)
    except WyzeApiError as e:
        # You will get a WyzeApiError is the request failed
        print(f"Got an error: {e}")

def test_bulb(mac) :
    try:
      bulb = client.bulbs.info(device_mac=mac)
      print(f"type: {bulb.type}")
      print(f"model: {bulb.product.model}")
      print(f"power: {bulb.is_on}")
      print(f"online: {bulb.is_online}")
      print(f"brightness: {bulb.brightness}")
      print(f"temp: {bulb.color_temp}")
      print(f"color: {bulb.color}")

      # client.bulbs.set_brightness(device_mac=bulb.mac, device_model=bulb.product.model, brightness=30)
      # client.bulbs.set_color(device_mac=bulb.mac, device_model=bulb.product.model, color='ff0000')
      client.bulbs.set_color_temp(device_mac=bulb.mac, device_model=bulb.product.model, color_temp=2356)

      # bulb = client.bulbs.info(device_mac=mac)
      # assert bulb.brightness == 100
      # assert bulb.color == 'ff00ff'
      # assert bulb.color_temp == 3800

      # client.bulbs.set_away_mode(device_mac=bulb.mac, device_model=bulb.product.model, away_mode=True)

    except WyzeApiError as e:
        # You will get a WyzeApiError is the request failed
        print(f"Got an error: {e}")

if __name__ == "__main__" :
    main()
