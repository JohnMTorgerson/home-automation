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

# # use the following when testing wyze_sdk from local fork
# import sys
# # insert at 1, 0 is the script path (or '' in REPL)
# sys.path.insert(1, '../!...Forks/wyze_sdk_fork')

# from wyze_sdk import Client
# from wyze_sdk.errors import WyzeApiError
#
# load_dotenv()
# client = Client(email=os.environ['WYZE_EMAIL'], password=os.environ['WYZE_PASSWORD'])

def main() :
    data = {
        "sunlight_values" : get_sunlight_values()
    }

    with open("data.json", "w") as f :
        json.dump(data, f)

def get_sunlight_values() :
    from scenes.timebased.sunlight import sunlight
    midnight = datetime.datetime.now(tz=ZoneInfo('US/Central')).replace(hour=0, minute=0, second=0, microsecond=0)
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

if __name__ == "__main__" :
    main()
