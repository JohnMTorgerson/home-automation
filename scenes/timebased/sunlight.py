from pprint import pprint
import datetime
from suntime import Sun, SunTimeException
import math

try:
    from zoneinfo import ZoneInfo
except:
    from backports.zoneinfo import ZoneInfo

# import wyze_sdk
# wyze_sdk.set_file_logger(__name__, 'tmp/log.log')



def run(client=None,bulbs=[],bulb_props={},now=None) :
    if client is None or isinstance(client,list) :
        raise Exception('Must pass client object to sunlight.run()')
        # pass

    minutes_since = get_relative_time(now)

    if minutes_since is not None:

        srt = minutes_since['sunrise']
        sst = minutes_since['sunset']

        # defaults in case of error
        temp = 2700
        brightness = 100

        try :
            temp = get_temp(srt,sst)
            brightness = get_brightness(srt,sst)
        except Exception as e:
            print(e)

        print(f"sunrise: {int(srt)} sunset: {int(sst)} --- temp: {temp} brightness: {brightness}")

        for bulb in bulbs:
            try:
                adjusted_temp = bulb_props.bulbs[bulb.nickname]["temp_adjust"](temp)
            except:
                print(f"Could not find adjusted temp for {bulb.nickname}")
                adjusted_temp = temp

            try:
                adjusted_brightness = bulb_props.bulbs[bulb.nickname]["brightness_adjust"](brightness)
            except:
                print(f"Could not find adjusted temp for {bulb.nickname}")
                adjusted_brightness = brightness

            client.bulbs.set_color_temp(device_mac=bulb.mac, device_model=bulb.product.model, color_temp=adjusted_temp)
            client.bulbs.set_brightness(device_mac=bulb.mac, device_model=bulb.product.model, brightness=adjusted_brightness)



    else:
        print("Could not get sunrise/sunset times")


    # for n in range(int(1621054800/60/30),int(1621141200/60/30)):
    #     time = datetime.datetime.fromtimestamp(n*30*60)
    #     times = get_relative_time(time)
    #     get_temp(times['sunrise'],times['sunset'])

def get_brightness(srt,sst) :
    return 75

def get_temp(srt,sst) :
    # sst is minutes since sunrise (so, negative if before sunrise)
    # sst is minutes since sunset (so, negative if before sunset)
    warmest = 2400 # 1800 is the minimum possible value for mesh bulbs
    coldest = 5900 # 6500 is the maximum possible value for mesh bulbs
    floor = warmest + 100
    ceiling = coldest - 100
    range = coldest - warmest
    steepness = 1/15 # unitless constant to adjust the steepness of the curve
    offset = 0 # positive offset makes changes happen later (in minutes). If 0, the steepest part of the curve will be right at sunrise/sunset
    temp = 2700 # just a default in case all the conditionals fail for some reason

    if range < 0:
        raise Exception('warmest temp must be a smaller value than coldest temp')

    # MIDNIGHT TO SUNRISE
    if srt < 0:
        print("MIDNIGHT TO SUNRISE")
        # temp = range * -1 * math.atan((offset - srt) * steepness)/math.pi + warmest + range/2
        temp = values_curve(srt,offset=offset,low=warmest,high=coldest,steepness=steepness,direction='ascending',floor=floor,ceiling=ceiling)
    # SUNRISE TO MIDDAY
    elif srt >= 0 and sst < 0 and abs(srt) < abs(sst):
        print("SUNRISE TO MIDDAY")
        # temp = range * -1 * math.atan((offset - srt) * steepness)/math.pi + warmest + range/2
        temp = values_curve(srt,offset=offset,low=warmest,high=coldest,steepness=steepness,direction='ascending',floor=floor,ceiling=ceiling)
    # MIDDAY to SUNSET
    elif srt > 0 and sst < 0 and abs(srt) >= abs(sst):
        print("MIDDAY to SUNSET")
        # temp = range * math.atan((offset - sst) * steepness)/math.pi + warmest + range/2
        temp = values_curve(sst,offset=offset,low=warmest,high=coldest,steepness=steepness,direction='descending',floor=floor,ceiling=ceiling)
    # SUNSET TO MIDNIGHT
    elif srt > 0 and sst >= 0:
        print("SUNSET TO MIDNIGHT")
        # temp = range * math.atan((offset - sst) * steepness)/math.pi + warmest + range/2
        temp = values_curve(sst,offset=offset,low=warmest,high=coldest,steepness=steepness,direction='descending',floor=floor,ceiling=ceiling)

    # temp = range * math.atan((offset - time) * steepness)/math.pi + warmest + range/2

    return temp

def values_curve(time,offset=0,low=0,high=100,steepness=1/15,direction='descending',floor=float('-inf'),ceiling=float('inf')):
    '''
    Create a value (e.g. temp or brightness) based on the arctan of a given time input; arctan is used in order to generate a smooth curve between high and low horizontal asymptotes

    :param int time: the time (in minutes) since event, i.e. sunrise/sunset (so, time is negative if event is in the future)
    :param int offset: slide the curve earlier or later relative to time_anchor; positive offset makes changes happen later (in minutes)
    :param int low: the lower asymptote limit
    :param int high: the upper asymptote limit
    :param float floor: an optional hard minimum, clipping the lower asymptote limit
    :param float ceiling: an optional hard maximum, clipping the upper asymptote limit
    :param float steepness: a unitless constant to adjust the steepness of the curve
    :param str direction: should be either 'descending' or 'ascending', adjusts direction of curve

    :return: the value (e.g. temp or brightness)
    :rtype: int

    :raises ValueError: if low > high
    :raises ValueError: if floor > ceiling
    '''

    range = high - low
    if range < 0:
        raise ValueError('min (warmest temp or lowest brightness) must be a smaller value than max (coolest temp or highest brightness)')

    if floor > ceiling:
        raise ValueError('floor must be less than or equal to ceiling')

    direction = 1 if direction == 'descending' else -1
    return int(min(ceiling,max(floor,direction * range * math.atan((offset - time) * steepness)/math.pi + low + range/2)))

def get_relative_time(now=datetime.datetime.now(tz=ZoneInfo('US/Central'))):
    try :
        latitude = 45
        longitude = -93

        sun = Sun(latitude, longitude)

        # today = datetime.datetime.now().date()
        # now = datetime.datetime(2011, 10, 26, 18, 0, 0)
        print(f"Now: {now}")

        sunrise = sun.get_local_sunrise_time(now)#.replace(tzinfo=ZoneInfo('US/Central'))
        # print(f"Sunrise: {sunrise}")
        # sunset = sun.get_local_sunset_time(now).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/Chicago'))
        # sunset = sun.get_local_sunset_time(now).replace(tzinfo=datetime.timezone.utc).astimezone(ZoneInfo('US/Central'))
        sunset = sun.get_local_sunset_time(now)
        # bug workaround:
        if sunset < sunrise:
            sunset = sunset + datetime.timedelta(1)
        # print(f"Sunset: {sunset}")
        # print('On {} the sun rose at {} and set at {}.'.
        #       format(today, sunrise.strftime('%H:%M'), sunset.strftime('%H:%M')))

        # delta = datetime.timedelta(hours=1)
        sr_delta = (now.timestamp() - sunrise.timestamp()) / 60 # number of minutes since sunrise
        ss_delta = (now.timestamp() - sunset.timestamp()) / 60 # number of minutes since sunset
        # print(f"Sunrise was {int(sr_delta / 6) / 10} hours ago")
        # print(f"Sunset was {int(ss_delta / 6) / 10} hours ago")

        time_since = {
            "sunrise": sr_delta,
            "sunset": ss_delta
        }

    except SunTimeException as e:
        print(f"Problem getting sunrise/sunset times: {e}")
    else:
        return time_since

if __name__ == "__main__" :
    run()
