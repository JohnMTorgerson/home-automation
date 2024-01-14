import os
import inspect
import logging
import csv
import requests
from requests.exceptions import HTTPError
from datetime import datetime, timezone
try:
    from zoneinfo import ZoneInfo
except:
    from backports.zoneinfo import ZoneInfo
import json

# create logger
logger = logging.getLogger(f"HA.{__name__}")

path_ = os.path.dirname(inspect.getabsfile(inspect.currentframe())) # actual path of the script's directory, regardless of where it's being called from
data_path = f"{path_}/data/weather_data.json"

def fetch_and_save(save_filepath=data_path, num_days=1, force=False):
    mins_to_wait = 90
    # ''force'' forces a fetch regardless of how long it's been since the last try;
    # if false, we only check if the last entry is over 1 hour old
    # (since that's how often the source seems to be updated)
    now = round(datetime.now().timestamp()*1000)
    last_entry_time = get_last_entry_time()
    # logger.debug(f"(latest + {mins_to_wait}min) {last_entry_time + mins_to_wait * 60 * 1000} vs. (now) {now}")

    if not force and last_entry_time + mins_to_wait * 60 * 1000 > now :
        logger.debug(f"latest entry is <= {mins_to_wait}min old, so NOT fetching weather data)")
        return
    elif force :
        logger.debug("force==True, so fetching weather data...")
    else :
        logger.debug(f"last entry >= {mins_to_wait}min old, so fetching weather data...")

    logger.info("Fetching and saving weather data...")

    # unknown what the maximum allowed value is for num_days; the highest example on the website is 56 days
    data_url = f'https://weather.gladstonefamily.net/cgi-bin/wxobservations.pl?site=KMSP&days={num_days}'
    data = download(data_url)
    dict_data = convert_to_dict(data)
    save_to_file(dict_data, save_filepath, last_entry_time)

# download data
def download(url):
    try:
        response = requests.get(url)

        # tell the response to raise an error if the request was not successful
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')
    else:
        logger.debug('Success retrieving weather data')
        # logger.debug(response.text)
        return response.text

# open csv data
# and convert it to a dict object
def convert_to_dict(csv_data):
    dict_data_list = csv.DictReader(csv_data.splitlines())
    dict_data_keyval = {}
    for row in dict_data_list :
        # read the time data and convert to a datetime object
        try:
            time = datetime.strptime(row["Time (UTC)"], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).astimezone(tz=ZoneInfo('US/Central'))
        except ValueError as e:
            logger.error(f'Skipping data point, could not parse date string: {row["Time (UTC)"]}\n{e}')
            continue

        # add row to dict_data_keyval using the Unix timestamp as a key
        dict_data_keyval[round(time.timestamp()*1000)] = row

    logger.debug("Success formatting data")

    # logger.debug(JSON.dumps(dict_data_keyval))
    return dict_data_keyval

# save the converted json data to a file for later access
# write json data to file at filepath, adding to existing data (overwriting any duplicate dates)
def save_to_file(new_data, filepath=data_path, last_entry_time=float('inf')):
    # first open existing file and get old data
    data = read_from_file(filepath)

    # loop through the new data
    new_entries_found = 0
    for timestamp in new_data:
        # and add it to the existing data, overwriting any duplicate entries
        # we have to convert the key to a string in order to match the json data from the file
        # or else, for any overlapping data, we'll end up with duplicate entries (some int keys and some string keys)
        data[str(timestamp)] = new_data[timestamp]

        if timestamp > last_entry_time :
            new_entries_found += 1

    logger.debug(f"Fetched {new_entries_found} new entries")

    # write the combined data back to the file
    with open(filepath,'w') as f:
        json.dump(data, f)

    logger.debug("Success writing to file")


def read_from_file(filepath=data_path) :
    try:
        with open(filepath,'r') as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError as e:
                logger.error(f'Error loading data from {filepath}: {e}')

                if not f.read(1):
                    logger.warning('File exists but is empty')
                    data = {}
                else:
                    raise e

    except FileNotFoundError as e:
        logger.error("No existing data file found; creating new one")
        data = {}

    return data

def get_last_entry_time(filepath=data_path) :
    data = read_from_file(filepath)
    latest = 0
    for timestamp in data :
        timestamp = int(timestamp)
        if timestamp > latest :
            latest = timestamp

    # logger.debug(f"latest == {latest}")

    return latest        

if __name__ == "__main__" :
    # log to console at DEBUG level
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(name)s.%(funcName)s() line %(lineno)s %(levelname).5s :: %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    fetch()
