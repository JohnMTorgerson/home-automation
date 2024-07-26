import logging
import get_devices
from devices import device_props
from pprint import pprint
# from wyze_sdk import Client

# create logger
logger = logging.getLogger(f"HA.{__name__}")


# ========== BULBS ========== #
# get bulbs for lighting scenes
def get(client, rooms=None) :
    if rooms is not None :
        # if a list of rooms was specified,
        # return list of bulbs in that room
        try:
            bulbs = get_devices.get_by_type(client,'MeshLight')
            return [bulb for bulb in bulbs if bulb["room"] in rooms]
        except:
            logger.warning(f"Could not get bulbs (bad client object), returning empty list of bulbs")
            return []

    else :
        # if no rooms were provided,
        # return a dictionary of ALL bulbs (organized by room)

        bulbs = {
            "all": [],
            "living_room" : [],
            "kitchen" : [],
            "bedroom" : []
        }

        try:

            bulbs["all"] = get_devices.get_by_type(client,'MeshLight')

            # bulbs["living_room"] = list(filter(lambda b : bulb_props.bulbs[b.nickname]["room"] == "Living Room",bulbs))
            for bulb in bulbs["all"] :
                # print(bulb.nickname)

                b_prop = device_props.bulb_props.bulbs.get(bulb.nickname) # safe if there is no bulb of that nickname

                pprint(b_prop)

                if b_prop :
                    # living room bulbs
                    if b_prop["room"] == "Living Room" :
                        bulbs["living_room"].append(bulb)
                    # kitchen bulbs
                    if b_prop["room"] == "Kitchen" :
                        bulbs["kitchen"].append(bulb)
                    # bedroom bulbs
                    if b_prop["room"] == "Bedroom" :
                        bulbs["bedroom"].append(bulb)
        
        except:
            logger.warning(f"Could not get bulbs (bad client object), returning empty list of bulbs")

        # pprint(bulbs)

        return bulbs

def filter_by_group(bulbs,grp_name=None) :
    if grp_name is None :
        return bulbs
    
    def grp_filter(bulb) :
        try:
            return grp_name in device_props.bulb_props.bulbs[bulb.nickname]["groups"]
        except KeyError as e:
            return False
        
    return list(filter(grp_filter, bulbs))
