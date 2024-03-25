import logging
import os
from dotenv import load_dotenv
import datetime
from suntime import Sun, SunTimeException
import json
import inspect
import asyncio
from .daytimes import Daytimes
from . import move_shades

# from daytimes import Daytimes
# import move_shades


# print("__package__, __name__ ==", __package__, __name__)

# actual path of the script's directory, regardless of where it's being called from
path_ = os.path.dirname(inspect.getabsfile(inspect.currentframe()))
record_path = f"{path_}/record.json"

try:
    from zoneinfo import ZoneInfo
except:
    from backports.zoneinfo import ZoneInfo

# import wyze_sdk
# wyze_sdk.set_file_logger(__name__, 'tmp/log.log')

# create logger
shades_logger = logging.getLogger(f"HA.{__name__}")

try:
    load_dotenv()
    latitude = float(os.environ['LAT'])
    longitude = float(os.environ['LON'])
    timezone = os.environ['ZONE']
except Exception as e:
    raise Exception(f"Error: could not load latitude and longitude from environment") from e
    # shades_logger.error(f"Error: could not load latitude and longitude from environment: {e}")



def run(now=datetime.datetime.now(tz=ZoneInfo(timezone))):#client=None,bulbs=[],bulb_props={},now=None) :
#     asyncio.run(_run(now))

# async def _run(now):
    shades_logger.info('Running shades scene...')

    # get current time of day relative to sunrise and sunset (enumerated by a Daytime enum)
    daytime = get_daytime(now)

    # check today's record
    record = check_todays_record()
    current = check_current_state_record()

    if not current or current not in ["down","up"] :
        shades_logger.error(f"no current state found or unrecognized value ({current}), so doing nothing")
        return
    
    # if before sunrise, do nothing
    if daytime == Daytimes.MORNING:
        shades_logger.debug("MORNING, not sunrise yet, so doing nothing")
        return

    # if after sunrise and before sunset and no record yet for today, and current state is "down"
    if daytime == Daytimes.DAY:
        # we expect no record for the day if it's the first run since sunrise
        if not record:
            if current == "down":
                shades_logger.debug("DAY, and no record yet for today, and current state is 'down', so moving shades up")
                # move shades up
                success = send_move_request("up")
                if success:
                    # write new "up" record for today
                    write_todays_record({"up":str(now)})
            elif current == "up":
                shades_logger.warning("DAY, and no record yet for today, but current state is 'up', so doing nothing")
            return
        # if we've moved the shades up already today, do nothing
        if record and current == "up":
            shades_logger.debug("DAY, record found, and current state is 'up', so doing nothing")
            return


    # if after sunset
    if daytime == Daytimes.NIGHT :        
        # if there is no record for today, or if the record says we already moved the shades down,
        if not record or "down" in record.keys() :
            # do nothing
            shades_logger.debug("NIGHT, but no record found for today or already moved shades down, doing nothing")
            return
        # if there is an "up" record (but not down) and current state says we're up,
        if record["up"] and "down" not in record.keys():
            if current == "up" :
                shades_logger.debug("NIGHT, up record found for today but no down record, and current state is 'up', so moving shades down")
                # move shades down
                success = send_move_request("down")
                if success:
                    # write new "up/down" record for today
                    write_todays_record({"down":str(now)})
            elif current == "down":
                shades_logger.warning("NIGHT, and found 'up' record, but not 'down' record, HOWEVER current state is 'down', so doing nothing")

            return

    shades_logger.warning(f"NO CONDITIONS SATISFIED, doing nothing ::: time of day: {str(daytime)} ::: today's record: {json.dumps(record)} ::: current state: {current}")

def get_user_settings() :
    try:
        with open(f"{path_}/settings.json", "r") as f :
            settings = json.load(f)
    except Exception as e:
        shades_logger.error(f"Error: Unable to retrieve shades user settings from file. Temporarily using defaults\n{e}")
        # turn off if unable to read settings
        settings = {
            "on" : False,
        }

    shades_logger.info(f"Shades settings: {settings}")

    return settings

def write_todays_record(todays_record,now=datetime.datetime.now(tz=ZoneInfo(timezone))) :
    with open(record_path, "r+") as f :
        records = json.load(f)
        today = str(now.date())

        try:
            records[today] |= todays_record # try merging first
        except KeyError as e:
            records[today] = todays_record # we'll get here if this is the first record for today

        try:
            f.truncate(0)
            f.seek(0)
            json.dump(records,f,indent=4)
            shades_logger.info(f"writing record: {json.dumps(todays_record)}")
        except Exception as e:
            shades_logger.error(f"failed to write today's record to file: {repr(e)}")

def write_current_state_record(state) :
    with open(record_path, "r+") as f :
        records = json.load(f)

        records["current_state"] = state

        try:
            f.truncate(0)
            f.seek(0)
            json.dump(records,f,indent=4)
            shades_logger.info(f"writing current state: \"{state}\"")
        except Exception as e:
            shades_logger.error(f"failed to write current state to record file: {repr(e)}")


def check_todays_record(now=datetime.datetime.now(tz=ZoneInfo(timezone))) :
    with open(record_path, "r") as f :
        records = json.load(f)
        today = str(now.date())

        try:
            return records[today]
        except KeyError as e:
            return False
        
def check_current_state_record() :
    with open(record_path, "r") as f :
        records = json.load(f)

        try:
            return records["current_state"]
        except KeyError as e:
            shades_logger.error("could not find current state in record")
            return False


def get_daytime(now) :
    '''
    returns a Daytime enum (morning, day, or night) based on current time relative to sunrise and sunset
    '''

    minutes_since = get_relative_time(now)
    srt = minutes_since['sunrise']
    sst = minutes_since['sunset']

    # MIDNIGHT TO SUNRISE (i.e. MORNING)
    if srt < 0:
        return Daytimes.MORNING

    # SUNRISE TO SUNSET (i.e. DAY)
    if srt >= 0 and sst < 0:
        return Daytimes.DAY

    # SUNSET TO MIDNIGHT (i.e. NIGHT)
    if srt > 0 and sst >= 0:
        return Daytimes.NIGHT
    
    return None

def get_relative_time(now=datetime.datetime.now(tz=ZoneInfo(timezone))):
    '''
    get time deltas from 'now' relative to today's sunrise and sunset time
    (as well as the absolute sr and ss times for today)
    '''

    try :
        sun = Sun(latitude, longitude)

        # now = datetime.datetime(2022, 3, 14, 20, 15, 0)
        # now = now + datetime.timedelta(1)
        shades_logger.debug(f"Now: {now}")

        sunrise = sun.get_local_sunrise_time(now)#.replace(tzinfo=ZoneInfo(timezone))
        shades_logger.debug(f"Sunrise: {sunrise}")
        # sunset = sun.get_local_sunset_time(now).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/Chicago'))
        # sunset = sun.get_local_sunset_time(now).replace(tzinfo=datetime.timezone.utc).astimezone(ZoneInfo(timezone))
        sunset = sun.get_local_sunset_time(now)
        # bug workaround:
        if sunset < sunrise:
            sunset = sunset + datetime.timedelta(1)
        shades_logger.debug(f"Sunset: {sunset}")
        shades_logger.debug('On {} the sun rose at {} and set at {}.'.
              format(now.date(), sunrise.strftime('%H:%M'), sunset.strftime('%H:%M')))

        # delta = datetime.timedelta(hours=1)
        sr_delta = (now.timestamp() - sunrise.timestamp()) / 60 # number of minutes since sunrise
        ss_delta = (now.timestamp() - sunset.timestamp()) / 60 # number of minutes since sunset
        shades_logger.debug(f"Sunrise was {int(sr_delta / 6) / 10} hours ago")
        shades_logger.debug(f"Sunset was {int(ss_delta / 6) / 10} hours ago")

        data = {
            "sunrise": sr_delta,
            "sunset": ss_delta,
            "sunrise_abs": sunrise,
            "sunset_abs": sunset
        }

    except SunTimeException as e:
        shades_logger.error(f"Problem getting sunrise/sunset times: {e}")
    else:
        return data

def send_move_request(dir) :
    shades_logger.info(f"moving shades {dir}")

    try:
        response = move_shades.request(dir)
        shades_logger.debug(f"server response: {response}")
        if "Success" in response :
            write_current_state_record(dir)
            return True
    except Exception as e:
        shades_logger.error(f"problem requesting shades move: {repr(e)}")
        return False

    return False

# def clamp(value,range) :
#     return max(range[0],min(range[1],value))

if __name__ == "__main__" :
    run()
