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
    from scenes.basic.thermostat import get_data
except ModuleNotFoundError as e :
    print("Unable to import get_data")

try :
    from scenes.basic.thermostat import thermostat
except ModuleNotFoundError as e :
    print("Unable to import thermostat")



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
        current_sensor_values = get_data.get_current(log=False)
    except Exception as e :
        current_sensor_values = {"temp_c":None,"temp_f":None,"humidity":None}

    logged_weather_data = get_data.get_logged_weather_data(day_range=7)
    logged_sensor_values = get_data.get_logged_sensor_data(day_range=7)

    therm_settings = thermostat.get_user_settings()

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
                "settings" : therm_settings,
                "current" : {
                    "temp_c" : current_sensor_values["temp_c"],
                    "temp_f" : current_sensor_values["temp_f"],
                    "humidity" : current_sensor_values["humidity"]
                },
                "logged_sensor" : logged_sensor_values,
                "logged_weather" : logged_weather_data
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
