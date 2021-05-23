import os
from pprint import pprint

# use the following when testing wyze_sdk from local fork
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../!...Forks/wyze_sdk_fork')

from wyze_sdk.errors import WyzeApiError

# import wyze_sdk
# wyze_sdk.set_file_logger(__name__, 'tmp/log.log')


def get_all(client) :
    response = []

    try:
        response = client.devices_list()
        # for device in client.devices_list():
        # #     # print(f"mac: {device.mac}")
        # #     # print(f"nickname: {device.nickname}")
        # #     # print(f"is_online: {device.is_online}")
        # #     # print(f"product model: {device.product.model}")
        #     pprint(device)

    except WyzeApiError as e:
        # You will get a WyzeApiError if the request failed
        raise

    return response


def get_by_type(client,type) :
    response = []

    try:
        response = list(filter(lambda d : d.type == type,client.devices_list()))

    except WyzeApiError as e:
        # You will get a WyzeApiError if the request failed
        raise

    return response
