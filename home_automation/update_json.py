import os
import logging
from dotenv import load_dotenv
import json
import math
import datetime
try:
    from zoneinfo import ZoneInfo
except:
    from backports.zoneinfo import ZoneInfo

logger = logging.getLogger(f"HA.{__name__}")

try :
    from scenes.sunlight import sunlight
except ModuleNotFoundError as e :
    logger.error("Unable to import sunlight")

try :
    from scenes.color import color
except ModuleNotFoundError as e :
    logger.error("Unable to import color")

try :
    from scenes.thermostat import get_data
except ModuleNotFoundError as e :
    logger.error("Unable to import get_data")

try :
    from scenes.thermostat import thermostat
except ModuleNotFoundError as e :
    logger.error("Unable to import thermostat")



now = datetime.datetime.now(tz=ZoneInfo('US/Central'))# + datetime.timedelta(days=183)
midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)


def update() :
    logger.debug("Updating json!!!")
    # we can get the current "sunlight" scene values without actually affecting the bulbs by passing empty values
    current_sunlight_values = sunlight.run(client=None,bulbs=[],bulb_props={},now=now,log=False)

    try :
        current_sensor_values = thermostat.get_current_values(log=False)
    except Exception as e :
        current_sensor_values = {"temp_c":None,"temp_f":None,"rel_hum":None,"abs_hum":None}

    logged_weather_data = get_data.get_logged_weather_data(hour_range=25)
    logged_sensor_values = get_data.get_logged_sensor_data(day_range=7)

    therm_settings = thermostat.settings.get()
    sunlight_settings = sunlight.get_user_settings()
    color_settings = color.get_user_settings()

    data = {
        "scenes" : {
            "sunlight" : {
                "settings" : sunlight_settings,
                "current_system_time" : now.timestamp(),
                "current_temp" : current_sunlight_values[0],
                "current_brightness" : current_sunlight_values[1],
                "sunlight_curve" : get_sunlight_values(),
                "suntimes" : get_suntimes()
            },
            "color" : {
                "settings": color_settings
            },
            "thermostat" : {
                "settings" : therm_settings,
                "current" : {
                    "temp_c" : current_sensor_values["temp_c"],
                    "temp_f" : current_sensor_values["temp_f"],
                    "rel_hum" : current_sensor_values["rel_hum"],
                    "abs_hum" : current_sensor_values["abs_hum"]
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

    # logger.debug(json.dumps(values))
    return values

# get today's sunrise and sunset times
def get_suntimes() :
    values = sunlight.get_relative_time(now)
    sunrise = values["sunrise_abs"].timestamp() - midnight.timestamp()
    sunset = values["sunset_abs"].timestamp() - midnight.timestamp()

    return [sunrise, sunset]

if __name__ == "__main__" :
    update()
