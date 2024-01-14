# print("__package__, __name__ ==", __package__, __name__)
import logging
from datetime import datetime

# must use 'from .' for when the automation gui accesses this module
from . import fetch_weather_data
from . import get_data
from . import write_data
from . import settings

# create logger
therm_logger = logging.getLogger(f"HA.{__name__}")


def run(client=None,plugs={}) :

    plugs_is_empty = True
    for list_of_plugs_by_controlling in plugs :
        if len(list_of_plugs_by_controlling) > 0 :
            plugs_is_empty = False
    if client == None or plugs_is_empty :
        return

    therm_logger.info("Running thermostat scene...")

    # fetch and save weather data (used by automation-gui)
    fetch_weather_data.fetch_and_save()

    # get thermostat settings
    settings_ = settings.read()

    # if this is the first time the scene has been run after midnight,
    # we want to record the current target values in the thermostat data file;
    # the reason for this is so the automation-gui can get an update on what
    # they are every day (in case they haven't been changed manually in a while)
    # we have to do this check BEFORE checking current values or the check will always fail
    if first_run_of_day() :
        therm_logger.debug("Writing out temp_target and rel_hum_max into data.txt ...")
        write_data.new_ctrl_change_record(datetime.now(),{
            "temp_target" : temp_target,
            "rel_hum_max" : settings_["rel_hum_max"]
        })


    # get current values from sensor(s)
    values = get_current_values()
    temp = values["temp_f"]
    if settings_["use_abs_humidity"] :
        humidity = values["abs_hum"]
    else :
        humidity = values["rel_hum"]


    # get target values set by user for both temp and humidity
    temp_hum_cutoff =   settings_["temp_hum_cutoff"]
    temp_target =       settings_["temp_target"]
    temp_hyst =         settings_["temp_hyst"]
    if settings_["use_abs_humidity"] :
        hum_units = "g/m³"
        hum_max =           settings_["abs_hum_max"]
        hum_min =           settings_["abs_hum_min"]
        hum_hyst =          settings_["abs_hum_hyst"]
    else :
        hum_units = "%"
        hum_max =           settings_["rel_hum_max"]
        hum_min =           settings_["rel_hum_min"]
        hum_hyst =          settings_["rel_hum_hyst"]

    # if thermostat is set to off, turn plugs off and return
    if (settings_["on"] == False) :
        therm_logger.info(f'************* THERMOSTAT IS SET TO OFF, (turning all devices off)')
        switchAC(value="off",client=client, plugs=plugs)
        switchHumidifier(value="off",client=client, plugs=plugs)
        return

    # turn A/C on or off based on temp and humidity targets vs current sensor values
    def run_AC() :
        if (temp <= temp_target - temp_hyst) and (humidity <= hum_max - hum_hyst or temp < temp_hum_cutoff):
            # turn off A/C
            therm_logger.info(f'Temp is {temp}, {(temp_target-temp):.1f}° below target; Humidity is {humidity}, {(hum_max-humidity):.1f} below max: TURNING A/C OFF')
            switchAC(value="off",client=client, plugs=plugs)
        elif (temp > temp_target) or (humidity > hum_max and temp >= temp_hum_cutoff):
            # turn on A/C
            therm_logger.info(f'Temp is {temp}, {(temp-temp_target):.1f}° above target; Humidity is {humidity}, {(humidity-hum_max):.1f} above max: TURNING A/C ON')
            switchAC(value="on",client=client, plugs=plugs)
        else :
            # within hysteresis range, so do nothing
            therm_logger.info(f"Temp and humidity are both below target or within hysteresis range ({(temp_target-temp):.1f}° below temp target, {(hum_max-humidity):.1f} {hum_units} below humidity target), not changing A/C state")

    # turn Humidifier on or off based on temp and humidity targets vs current sensor values
    def run_Humidifier() :
        # if above minimum turn humidifier off
        if (humidity >= hum_min + hum_hyst):
            # turn off Humidifier
            therm_logger.info(f'Humidity is {humidity:.2f}, {(humidity-hum_min):.2f} above min: TURNING HUMIDIFIER OFF')
            switchHumidifier(value="off",client=client, plugs=plugs)
        # else if below minimum, minus hysteresis value, turn humidifier on
        elif (humidity < hum_min):
            # turn on Humidifier
            therm_logger.info(f'Humidity is {humidity:.2f}, {(hum_min-humidity):.2f} below min: TURNING HUMIDIFIER ON')
            switchHumidifier(value="on",client=client, plugs=plugs)
        else :
            # within hysteresis range, so do nothing, do not change state
            therm_logger.info(f"Humidity is within hysteresis range ({(hum_min):.2f}{hum_units} <= {(humidity):.2f}{hum_units} < {hum_min+hum_hyst}{hum_units}, not changing Humidifier state")

    # run A/C (if thresholds merit)
    run_AC()

    # run Humidifier (if thresholds merit)
    run_Humidifier()


def get_current_values(log=True) :
    # the optional 'log' param indicates primarily whether, when checking the sensor values,
    # get_data.get_current() should also save those values to data.txt;
    # when running the thermostat scene, we do want to do that,
    # but when this function is called from update_json.py, we pass log=False because we don't need to do it again;
    #
    # we also take advantage of the variable here to determine whether the logger should log any messages in this function;
    # we realize that may be confusing, hence this comment
    try :
        values = get_data.get_current(log) # gets current sensor values, but also logs them to ./data/data.txt
        if log : therm_logger.info(f"CURRENT VALUES ==== {str(values)}") #temp_c:{values['temp_c']}, temp_f:{values['temp_f']}, rel_hum:{values['rel_hum']}, abs_hum:{values['abs_hum']}")
    except (ModuleNotFoundError, NotImplementedError) as e :
        if log : therm_logger.error(f"Unable to read current sensor values... ({repr(e)})")

        # if not running on raspberry pi with 'board' module, just use most recent values that were logged
        try:
            values = get_data.get_most_recent_sensor_data()[1]
            values['temp_f'] = values['temp']
            values['temp_c'] = round((values['temp_f'] - 32) * 5/9,1)
            values['abs_hum'] = 0
            if log : therm_logger.error(f"...using most recent logged values instead:")
        except:
            if log : therm_logger.error("...and unable to read most recent sensor values, so using dummy values (for testing):")
            values = {'temp_c': 24, 'temp_f': 80.6, 'rel_hum': 45, 'abs_hum': 11.55}

        if log : therm_logger.debug(str(values)) # f"temp_c:{values['temp_c']}, temp_f:{values['temp_f']}, rel_hum:{values['rel_hum']}, abs_hum:{values['abs_hum']}"


    except Exception as e :
        therm_logger.error(f"Other error getting temp/humidity values: {repr(e)}")
        raise e

    return values

def switchAC(value="", client=None, plugs=[]) :
    previous_value = "off"

    therm_logger.debug(f"Turning {value} plugs:")
    try :
        for plug in plugs["A/C"] :
            # if any of the plugs were on already, we return that to the calling function
            if client.plugs.info(device_mac=plug.mac).is_on :
                previous_value = "on"

            therm_logger.debug(plug.nickname)
            if value == "off" :
                client.plugs.turn_off(device_mac=plug.mac, device_model=plug.product.model)
            elif value == "on" :
                client.plugs.turn_on(device_mac=plug.mac, device_model=plug.product.model)

        # only log the change if it actually changed irl
        if previous_value != value:
            log_switch(value, "A/C")
    except KeyError as e :
        therm_logger.debug(f"No A/C plugs found")

def switchHumidifier(value="", client=None, plugs=[]) :
    previous_value = "off"

    therm_logger.debug(f"Turning {value} plugs:")
    try :
        for plug in plugs["Humidifier"] :
            # if any of the plugs were on already, we return that to the calling function
            if client.plugs.info(device_mac=plug.mac).is_on :
                previous_value = "on"

            therm_logger.debug(plug.nickname)
            if value == "off" :
                client.plugs.turn_off(device_mac=plug.mac, device_model=plug.product.model)
            elif value == "on" :
                client.plugs.turn_on(device_mac=plug.mac, device_model=plug.product.model)

        # only log the change if it actually changed irl
        if previous_value != value:
            log_switch(value, "HUMIDIFIER")
    except KeyError as e :
        therm_logger.debug(f"No Humidifier plugs found")


def log_switch(value, deviceName) :
    write_data.new_switch_record(datetime.now(),deviceName,value)

    # run get_current_values() again, just to make sure we log the current sensor values into the data file right after we switch the A/C on/off
    get_current_values()

def first_run_of_day() :
    midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        last_entry_time = get_data.get_most_recent_sensor_data(any_line=True)[0]
    except Exception as e:
        # if we couldn't get the last entry, just say this is the first of the day
        therm_logger.error(f"Could not get most recent sensor entry, assuming this is the first run of the day ({repr(e)})")
        return True
    
    if datetime.fromtimestamp(last_entry_time/1000) < midnight :
        therm_logger.debug("First run of the day!!")
        return True
    therm_logger.debug("NOT first run of the day")
    return False

if __name__ == "__main__" :
    run()
