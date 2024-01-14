import logging
import json
from datetime import datetime
import copy

from . import settings_filepath
from . import write_data

logger = logging.getLogger(f"HA.{__name__}")

def write(settings_update) :
    # logger.debug(f"SETTINGS UPDATE:\n{json.dumps(settings_update)}")

    # update settings.json
    try:
        with open(settings_filepath, "r+") as f :
            settings = json.load(f)
            old_settings = copy.deepcopy(settings)
            settings |= settings_update

            # delete file contents
            f.seek(0)
            f.truncate()

            # write updated data to file
            json.dump(settings, f)
            logger.debug("successfully updated thermostat settings in settings.json")

    except Exception as e:
        logger.error(f"Error writing update to settings.json: {repr(e)}")
        raise e
    
    try:
        # then, if any of the changes were to the following keys,
        # we want to log them into data.txt so that the gui can make
        # use of them for visual reference
        ctrl_change_keys_master = {"on","temp_target","rel_hum_max","rel_hum_min"}
        ctrl_change_keys = list(set(settings_update.keys()) & ctrl_change_keys_master) # compare update to set of relevant keys
        # logger.debug("CTRL_CHANGE_KEYS: " + str(ctrl_change_keys))
        if len(ctrl_change_keys) > 0 : # if any relevant keys were present in the update
            now = datetime.now()
            ctrl_changes = {}
            for key in ctrl_change_keys :
                if old_settings[key] != settings_update[key] : # and if they have different values than the old settings
                    ctrl_changes[key] = settings_update[key] # save each relevant, altered key/value pair into a new dict

            # logger.debug(f"CTRL_CHANGES: {str(ctrl_changes)}")

            if len(ctrl_changes.keys()) > 0 :
                write_data.new_ctrl_change_record(now,ctrl_changes) # log that data and the present time into data.txt
                logger.debug(f"successfully logged thermostat ctrl change ({json.dumps(ctrl_changes)}) to data.txt")

    except Exception as e:
        logger.error(f"Error writing control change to data.txt: {repr(e)}")
        raise e
        
    return settings

def save(settings_update) :
    return write(settings_update)

def read() :
    try:
        with open(settings_filepath, "r") as f :
            settings = json.load(f)
    except Exception as e:
        logger.error(f"Error: Unable to retrieve thermostat settings from file. Temporarily using defaults\n{e}")
        # default values designed to keep the A/C and Humidifier off until the problem is fixed
        settings = {
            "on" : False,
            "show_weather_temp_value": False,
            "show_weather_temp_graph": False,
            "show_weather_hum_value": False,
            "show_weather_hum_graph": False,
            "temp_hum_cutoff" : 100,
            "temp_target" : 212,
            "temp_hyst" : 1,
            "rel_hum_max" : 100,
            "rel_hum_min" : 0,
            "rel_hum_hyst" : 1,
            "use_abs_hum" : False,
            "abs_hum_max": 1000.0,
            "abs_hum_min": 0.0,
            "abs_hum_hyst": 1.0
        }

    logger.info(f"Thermostat settings: {settings}")

    return settings

def get() :
    return read()
