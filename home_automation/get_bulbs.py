import get_devices
from devices import device_props
# from wyze_sdk import Client

# ========== BULBS ========== #
# get bulbs for lighting scenes
def get(client) :
    bulbs = {
        "all": [],
        "living_room" : [],
        "bedroom" : []
    }

    bulbs["all"] = get_devices.get_by_type(client,'MeshLight')

    # bulbs["living_room"] = list(filter(lambda b : bulb_props.bulbs[b.nickname]["room"] == "Living Room",bulbs))
    for bulb in bulbs["all"] :
        b_prop = device_props.bulb_props.bulbs.get(bulb.nickname) # safe if there is no bulb of that nickname

        if b_prop :
            # living room bulbs
            if b_prop["room"] == "Living Room" :
                bulbs["living_room"].append(bulb)
            # bedroom bulbs
            if b_prop["room"] == "Bedroom" :
                bulbs["bedroom"].append(bulb)

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
