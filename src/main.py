import os
from dotenv import load_dotenv
from pprint import pprint
import datetime
try:
    from zoneinfo import ZoneInfo
except:
    from backports.zoneinfo import ZoneInfo
import get_devices
# import rooms
from devices import bulb_props

import logging
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
# log to file at INFO level
file_handler = logging.FileHandler('../logs/log.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# log to another file at ERROR level
error_file_handler = logging.FileHandler('../logs/error.log')
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(formatter)
logger.addHandler(error_file_handler)
# log to console at DEBUG level
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# # use the following when testing wyze_sdk from local fork
# import sys
# # insert at 1, 0 is the script path (or '' in REPL)
# sys.path.insert(1, '../!...Forks/wyze_sdk_fork')

from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError

# import wyze_sdk
# wyze_sdk.set_file_logger(__name__, 'tmp/log.log')

load_dotenv()

try:
    client = Client(email=os.environ['WYZE_EMAIL'], password=os.environ['WYZE_PASSWORD'])
except Exception as e:
    logger.critical(f"Could not get client. Aborting: {e}")
    raise e

##### SCENES #####
from scenes.timebased import sunlight

def main() :
    logger.info('=================================================================')

    # get devices
    bulbs = []
    lr_bulbs = []
    try:
        bulbs = get_devices.get_by_type(client,'MeshLight')
        lr_bulbs = list(filter(lambda b : bulb_props.bulbs[b.nickname]["room"] == "Living Room",bulbs))
    except WyzeApiError as e:
        logger.error(f"WyzeApiError retrieving bulbs: {e}")
    except Exception as e:
        logger.error(f"Other error retrieving bulbs: {e}")

    # run scenes on specified devices
    sunlight.run(client=client,bulbs=lr_bulbs,bulb_props=bulb_props,now=datetime.datetime.now(tz=ZoneInfo('US/Central'))) # adjust the temperature according to daylight


if __name__ == "__main__" :
    main()