import os
from dotenv import load_dotenv
from pprint import pprint
import json
import math
import datetime
try:
    from zoneinfo import ZoneInfo
except:
    from backports.zoneinfo import ZoneInfo

from scenes.timebased.sunlight import sunlight


now = datetime.datetime.now(tz=ZoneInfo('US/Central'))# + datetime.timedelta(days=183)
midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

# # use the following when testing wyze_sdk from local fork
# import sys
# # insert at 1, 0 is the script path (or '' in REPL)
# sys.path.insert(1, '../!...Forks/wyze_sdk_fork')

# from wyze_sdk import Client
# from wyze_sdk.errors import WyzeApiError
#
# load_dotenv()
# client = Client(email=os.environ['WYZE_EMAIL'], password=os.environ['WYZE_PASSWORD'])

def update() :
    current_values = sunlight.run(client=None,bulbs=[],bulb_props={},now=now)

    data = {
        "scenes" : {
            "sunlight" : {
                "current_system_time" : now.timestamp(),
                "current_temp" : current_values[0],
                "current_brightness" : current_values[1],
                "sunlight_curve" : get_sunlight_values(),
                "suntimes" : get_suntimes()
            }
         }
    }

    with open("data.json", "w") as f :
        json.dump(data, f)

def get_sunlight_values() :
    interval = 3 # in minutes
    delta = datetime.timedelta(minutes=interval)
    time = midnight
    values = {}
    for i in range(math.floor(24 * 60 / interval)) :
        value = sunlight.run(client=None,bulbs=[],bulb_props={},now=time)
        values[math.floor(time.timestamp() - midnight.timestamp())] = value
        time = time + delta

    # pprint(values)
    return values

def get_suntimes() :
    values = sunlight.get_relative_time(now)
    sunrise = values["sunrise_abs"].timestamp() - midnight.timestamp()
    sunset = values["sunset_abs"].timestamp() - midnight.timestamp()

    return [sunrise, sunset]

if __name__ == "__main__" :
    update()
