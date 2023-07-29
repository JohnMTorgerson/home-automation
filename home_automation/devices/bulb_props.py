min_temp = 1800
max_temp = 6500
min_b = 0
max_b = 100

bulbs = {
    "Globe":{
        "room":"Living Room",
        "brightness_adjust": lambda b,t=None : int(b/4),
        "temp_adjust": lambda t : max(t - 100,min_temp),
        "color_adjust": lambda c : c
    },
    "Floor Lamp":{
        "room":"Living Room",
        "brightness_adjust": lambda b,t=None : b,
        "temp_adjust": lambda t : t,
        "color_adjust": lambda c : c
    },
    "Wood Lamp":{
        "room":"Living Room",
        "brightness_adjust": lambda b,t=None : b,
        "temp_adjust": lambda t : min(t + 100,max_temp),
        "color_adjust": lambda c : c
    },
    "Left Window":{
        "room":"Living Room",
        "brightness_adjust": lambda b,t=None : b,
        "temp_adjust": lambda t : min(t + 250,max_temp),
        "color_adjust": lambda c : c
    },
    "Right Window":{
        "room":"Living Room",
        "brightness_adjust": lambda b,t=None : b,
        "temp_adjust": lambda t : min(t + 250,max_temp),
        "color_adjust": lambda c : c
    },
    "Ceiling N":{
        "room":"Living Room",
        "groups":["ceiling"],
        "sst_adjust": lambda sst : sst + 60, # to warm and dim earlier
        "srt_adjust": lambda srt : srt - 60, # to bright and cool later
        "brightness_adjust": lambda b,t=5000 : round(max_b * pow(b / max_b,2) * min(pow(t/5000,1),1)),
        "temp_adjust": lambda t : max(t - 200,min_temp),
        "on_adjust": lambda b : False if b < 8 else True,
        "color_adjust": lambda c : c
    },
    "Ceiling W":{
        "room":"Living Room",
        "groups":["ceiling"],
        "sst_adjust": lambda sst : sst + 60, # to warm and dim earlier
        "srt_adjust": lambda srt : srt - 60, # to bright and cool later
        "brightness_adjust": lambda b,t=5300 : round(max_b * pow(b / max_b,2) * min(pow(t/5300,1.5),1)),
        "temp_adjust": lambda t : max(t - 200,min_temp),
        "on_adjust": lambda b : False if b < 8 else True,
        "color_adjust": lambda c : c
    },
    "Ceiling S":{
        "room":"Living Room",
        "groups":["ceiling"],
        "sst_adjust": lambda sst : sst + 60, # to warm and dim earlier
        "srt_adjust": lambda srt : srt - 60, # to bright and cool later
        "brightness_adjust": lambda b,t=5300 : round(max_b * pow(b / max_b,2) * min(pow(t/5300,1.5),1)),
        "temp_adjust": lambda t : max(t - 200,min_temp),
        "on_adjust": lambda b : False if b < 8 else True,
        "color_adjust": lambda c : c
    },

    "Bathroom L":{
        "room":"Bathroom",
        "brightness_adjust": lambda b,t=None : b,
        "temp_adjust": lambda t : t,
        "color_adjust": lambda c : c
    },

    "Bedside":{
        "room":"Bedroom",
        "brightness_adjust": lambda b,t=None : b,
        "temp_adjust": lambda t : t,
        "color_adjust": lambda c : c
    }

}
