import get_devices
from devices import device_props
# from wyze_sdk import Client

def get(client) :
    plugs = {
        "all" : [],
        "thermostat" : {}
    }

    plugs["all"] = get_devices.get_by_type(client,'Plug')

    for plug in plugs["all"] :
        p_prop = device_props.plug_props.plugs.get(plug.nickname) # safe if there is no device of that nickname

        if p_prop :
            # specify plugs in which rooms should be controlled by thermostat
            if p_prop["room"] == "Living Room" or p_prop["room"] == "Kitchen" : # or p_prop["room"] == "Bedroom" :
                if p_prop["controlling"] not in plugs["thermostat"] :
                    plugs["thermostat"][p_prop["controlling"]] = []

                plugs["thermostat"][p_prop["controlling"]].append(plug)

    return plugs
