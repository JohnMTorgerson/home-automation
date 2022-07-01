import os
from dotenv import load_dotenv
load_dotenv()
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
file_handler = logging.FileHandler(os.path.abspath(f"{os.environ['LOG_PATH']}/log.log"))
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# log to another file at ERROR level
error_file_handler = logging.FileHandler(os.path.abspath(f"{os.environ['LOG_PATH']}/error.log"))
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(formatter)
logger.addHandler(error_file_handler)
# log to console at DEBUG level
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# null handler for modules to optionally log nothing
logging.getLogger('null').addHandler(logging.NullHandler())

# # use the following when testing wyze_sdk from local fork
# import sys
# # insert at 1, 0 is the script path (or '' in REPL)
# sys.path.insert(1, '../!...Forks/wyze_sdk_fork')

from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError

# import wyze_sdk
# wyze_sdk.set_file_logger(__name__, 'tmp/log.log')

# updates json data dump for the automation-gui to read from
import update_json
update_json.update()

try:
    client = Client(email=os.environ['WYZE_EMAIL'], password=os.environ['WYZE_PASSWORD'])
except Exception as e:
    logger.critical(f"Could not get client. Aborting: {e}")
    raise e

##### SCENES #####
from scenes.timebased.sunlight import sunlight
# from scenes.timebased import wakeup
from scenes.basic.thermostat import thermostat

def main() :
    logger.info('=================================================================')

    # ========== BULBS ========== #
    # get bulbs for lighting scenes
    bulbs = []
    lr_bulbs = []
    br_bulbs = []
    try:
        bulbs = get_devices.get_by_type(client,'MeshLight')
        # lr_bulbs = list(filter(lambda b : bulb_props.bulbs[b.nickname]["room"] == "Living Room",bulbs))
        for bulb in bulbs :
            b_prop = bulb_props.bulbs.get(bulb.nickname) # safe if there is no bulb of that nickname

            if b_prop :
                # living room bulbs
                if b_prop["room"] == "Living Room" :
                    lr_bulbs.append(bulb)
                # bedroom bulbs
                if b_prop["room"] == "Bedroom" :
                    br_bulbs.append(bulb)
    except WyzeApiError as e:
        logger.error(f"WyzeApiError retrieving bulbs: {e}")
    except Exception as e:
        logger.error(f"Other error retrieving bulbs: {e}")

    # ========== PLUGS ========== #
    # get plugs
    try:
        plugs = get_devices.get_by_type(client,'Plug')
        pprint(plugs)
    except WyzeApiError as e:
        logger.error(f"WyzeApiError retrieving plugs: {e}")
    except Exception as e:
        logger.error(f"Other error retrieving plugs: {e}")


    #  ===== run scenes on specified devices ===== #
    sunlight.run(client=client,bulbs=lr_bulbs,bulb_props=bulb_props,now=datetime.datetime.now(tz=ZoneInfo('US/Central'))) # adjust the temperature according to daylight
    # wakeup.run(client=client,bulbs=br_bulbs,bulb_props=bulb_props,now=datetime.datetime.now(tz=ZoneInfo('US/Central'))) # turn on and gradually brighten the bedroom bulbs according to when my alarm is set
    # thermostat.run()


if __name__ == "__main__" :
    main()
