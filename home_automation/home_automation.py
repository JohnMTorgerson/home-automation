import os
import sys
from dotenv import load_dotenv
load_dotenv()
from pprint import pprint
import datetime
import re
import pkgutil
try:
    from zoneinfo import ZoneInfo
except:
    from backports.zoneinfo import ZoneInfo

# print("__package__, __name__ ==", __package__, __name__)

# # use the following when testing wyze_sdk from local fork
# import sys
# # insert at 1: 0 is the script path (or '' in REPL)
# sys.path.insert(1, os.path.abspath('../../!...Forks/'))

from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError
# import wyze_sdk
# wyze_sdk.set_file_logger(__name__, 'tmp/log.log')

import login
import get_bulbs
import get_plugs
# import rooms
from devices import device_props
import update_json


# ========== SET UP LOGGING ========== #
import logging
logger = logging.getLogger('HA')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(name)s.%(funcName)s() line %(lineno)s %(levelname).5s :: %(message)s")
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
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
# null handler for modules to optionally log nothing
logging.getLogger('null').addHandler(logging.NullHandler())


# ========== GET WYZE CLIENT ========== #
try:
    # client = Client(email=os.environ['WYZE_EMAIL'], password=os.environ['WYZE_PASSWORD'])
    client = login.get_client()
except Exception as e:
    logger.critical(f"Could not get client. Aborting: {e}")
    raise e


##### SCENES #####
import scenes
from scenes.sunlight import sunlight
# from scenes.wakeup import wakeup
from scenes.color import color
from scenes.thermostat import thermostat
from scenes.thermostat.settings import write as thermostat_settings_change



# ========== GET DEVICES ========== #
# get bulbs for lighting scenes
try:
    bulbs = get_bulbs.get(client)
except WyzeApiError as e:
    logger.error(f"WyzeApiError retrieving bulbs: {e}")
except Exception as e:
    logger.error(f"Other error retrieving bulbs: {e}")

# get LED strips for lighting scenes
# (some code...)

# get plugs
try:
    plugs = get_plugs.get(client)
except WyzeApiError as e:
    logger.error(f"WyzeApiError retrieving plugs: {e}")
except Exception as e:
    logger.error(f"Other error retrieving plugs: {e}")


def main() :
    logger.info('=================================================================')

    #  ===== run scenes on specified devices ===== #
    sunlight_scene()
    thermostat_scene()

    # updates json data dump for the automation-gui to read from
    update_json.update()


################################

def scene(scene_name,grp_filter=None,**kwargs) :
    # make sure we have the required keyword arguments:
    try :
        required_kwargs = {
            "device":str,
            "rooms":list
        }
        for arg,type_ in required_kwargs.items() :
            assert arg in kwargs, f"Missing required keyword argument \"{arg}\""
            assert type(arg) == type_, f"\"{arg}\" must be a{'n' if (re.search('^[aeiou]',type_.__name__)) else ''} {type_.__name__}"
    except AssertionError as e :
        raise TypeError(e.args[0]) from None
    
    match device:
        case "bulb":
            filtered_bulbs = get_bulbs.filter_by_group(get_bulbs.get(client,rooms),grp_filter) # if grp_filter is None, will return all
        case "plug":
            pass
        case "led_strip":
            pass

    for scene in pkgutil.iter_modules(scenes.__path__) :
        print(scene.name)
        
    #    sunlight.run(client=client,bulbs=filtered_bulbs,bulb_props=device_props.bulb_props,now=datetime.datetime.now(tz=ZoneInfo('US/Central'))) # adjust the temperature according to daylight


def sunlight_scene(grp_filter=None) :
    try:
        filtered_bulbs = get_bulbs.filter_by_group(bulbs["living_room"],grp_filter) # if grp_filter is None, will return all
        sunlight.run(client=client,bulbs=filtered_bulbs,bulb_props=device_props.bulb_props,now=datetime.datetime.now(tz=ZoneInfo('US/Central'))) # adjust the temperature according to daylight
    except Exception as e :
        logger.error(f"Sunlight scene failed: {e}")

# this scene should not be run in main()
def color_scene(grp_filter=None) :
    try:
        filtered_bulbs = get_bulbs.filter_by_group(bulbs["living_room"],grp_filter) # if grp_filter is None, will return all
        color.run(client=client,bulbs=filtered_bulbs,bulb_props=device_props.bulb_props)
    except Exception as e :
        logger.error(f"Color scene failed: {e}")

# def wakeup_scene() :
#     wakeup.run(client=client,bulbs=bulbs["bedroom"],bulb_props=bulb_props,now=datetime.datetime.now(tz=ZoneInfo('US/Central'))) # turn on and gradually brighten the bedroom bulbs according to when my alarm is set

def thermostat_scene() :
    global client
    try:
        thermostat.run(client=client,plugs=plugs["thermostat"])
    except WyzeApiError as e :
        logger.debug('Thermostat scene failed: WyzeApiError')
        if str(e).startswith("The access token has expired") :
            logger.debug('Specifically, AccessTokenError')
            client = login.get_client()
            thermostat_scene()
    except Exception as e :
        logger.error(f"Thermostat scene failed: {repr(e)}")


if __name__ == "__main__" :
    main()
