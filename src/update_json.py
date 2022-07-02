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

try :
    from scenes.basic.thermostat import log_temp
except ModuleNotFoundError as e :
    print("Unable to import log_temp")



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
    # we can get the current "sunlight" scene values without actually affecting the bulbs by passing empty values
    current_sunlight_values = sunlight.run(client=None,bulbs=[],bulb_props={},now=now,log=False)
    try :
        current_therm_values = log_temp.get_and_log(log=False)
    except Exception as e :
        current_therm_values = {"temp_c":None,"temp_f":None,"humidity":None}

    data = {
        "scenes" : {
            "sunlight" : {
                "current_system_time" : now.timestamp(),
                "current_temp" : current_sunlight_values[0],
                "current_brightness" : current_sunlight_values[1],
                "sunlight_curve" : get_sunlight_values(),
                "suntimes" : get_suntimes()
            },
            "thermostat" : {
                "temp_c" : current_therm_values["temp_c"],
                "temp_f" : current_therm_values["temp_f"],
                "humidity" : current_therm_values["humidity"]
            }
        }
    }

    with open("data.json", "w") as f :
        json.dump(data, f)

# get "sunlight" scene bulb temp and brightness values for all times of day
def get_sunlight_values() :
    interval = 3 # in minutes
    delta = datetime.timedelta(minutes=interval)
    time = midnight
    values = {}
    for i in range(math.floor(24 * 60 / interval)) :
        value = sunlight.run(client=None,bulbs=[],bulb_props={},now=time,log=False)
        values[math.floor(time.timestamp() - midnight.timestamp())] = value
        time = time + delta

    # pprint(values)
    return values

# get today's sunrise and sunset times
def get_suntimes() :
    values = sunlight.get_relative_time(now)
    sunrise = values["sunrise_abs"].timestamp() - midnight.timestamp()
    sunset = values["sunset_abs"].timestamp() - midnight.timestamp()

    return [sunrise, sunset]

if __name__ == "__main__" :
    update()
