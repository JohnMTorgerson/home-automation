import logging

from . import therm_data_filepath

# create logger
logger = logging.getLogger(f"HA.{__name__}")

def new_sensor_record(time_,temp,rel_hum,abs_hum) :
    # ====== save the values to file ====== #
    new_record = f"{int(time_.timestamp()*1000)} {round(temp,1):04.1f} {round(rel_hum,1):04.1f} {round(abs_hum,1):04.1f} ({time_})\n"

    try:
        # check if new value is different from last recorded value
        with open(therm_data_filepath, "r") as f:
            last_line = f.readlines()[-1].split()
    except Exception as e:
        # last_line = [-1,-1,-1]
        logger.error(f"Unable to write sensor data to data.txt — {repr(e)}")
        return

    try:
        time_diff = (int(time_.timestamp()*1000) - int(last_line[0])) / 1000 / 60
        temp_diff = abs(float(last_line[1]) - temp)
        rel_hum_diff = abs(float(last_line[2]) - rel_hum)
        abs_hum_diff = abs(float(last_line[3]) - abs_hum)

        logger.debug(f"last sensor record: {last_line}")
        logger.debug(f'Differences:\ntime_diff: {time_diff}\ntemp_diff: {temp_diff}\nrel_hum_diff: {rel_hum_diff}\nabs_hum_diff: {abs_hum_diff}')

        # only log differences above the following thresholds
        if temp_diff >= 0.2 or rel_hum_diff > 0 or abs_hum_diff > 0 or time_diff > 30:
            # print(last_line)
            # print(float(last_line[1]))
            # print(float(last_line[2]))
            # print("different!!!!")

            # and then only log every 10 minutes unless the following thresholds are met
            if time_diff > 10 or temp_diff >= 0.5 or rel_hum_diff > 1 or abs_hum_diff > 0.2:
                logger.debug(f"diff thresholds met, writing new sensor record... (temp: {temp}º, hum: {rel_hum}%, {abs_hum}g/m³)")
                _write(new_record)

    except (ValueError, IndexError) as error:
        # if a line doesn't follow the format, (it's not a sensor record), then simply ignore it and write a new line
        _write(new_record)

def new_switch_record(time_,deviceName,value) :
    logger.debug(f"writing into {therm_data_filepath} that we turned {deviceName} {value}...")
    _write(f"{int(time_.timestamp()*1000)} [TURNED {deviceName} {value}] ({time_})\n")

def new_ctrl_change_record(time_,ctrl_changes) :
    for index, (key, val) in enumerate(ctrl_changes.items()):
    # for key,val in ctrl_changes.items() :
        _write(f"{int(time_.timestamp()*1000) + index} [SET {key} to {val}] ({time_})\n")

def _write(record) :
    try:
        with open(therm_data_filepath, "a") as f:
            f.write(record)
            # logger.debug("...successfully wrote to file!")
    except Exception as e :
        logger.error(f"Unable to write record \"{record}\" to therm data file: {e}")
        raise e
