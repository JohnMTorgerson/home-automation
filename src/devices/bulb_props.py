min_temp = 1800
max_temp = 6500
min_b = 0
max_b = 100

bulbs = {
    "Globe":{
        "room":"Living Room",
        "brightness_adjust": lambda b,t : int(b/4),
        "temp_adjust": lambda t : max(t - 100,min_temp)
    },
    "Floor Lamp":{
        "room":"Living Room",
        "brightness_adjust": lambda b,t : b,
        "temp_adjust": lambda t : t
    },
    "Wood Lamp":{
        "room":"Living Room",
        "brightness_adjust": lambda b,t : b,
        "temp_adjust": lambda t : min(t + 100,max_temp)
    },
    "Left Window":{
        "room":"Living Room",
        "brightness_adjust": lambda b,t : b,
        "temp_adjust": lambda t : min(t + 250,max_temp)
    },
    "Right Window":{
        "room":"Living Room",
        "brightness_adjust": lambda b,t : b,
        "temp_adjust": lambda t : min(t + 250,max_temp)
    },
    "Ceiling NE":{
        "room":"Living Room",
        "sst_adjust": lambda sst : sst + 60, # to warm and dim earlier
        "srt_adjust": lambda srt : srt - 60, # to bright and cool later
        "brightness_adjust": lambda b,t : int(max_b * pow(b / max_b,2) * min(pow(t/5000,1),1)),
        "temp_adjust": lambda t : max(t - 200,min_temp),
        "on_adjust": lambda b : False if b < 10 else True
    },
    "Ceiling NW":{
        "room":"Living Room",
        "sst_adjust": lambda sst : sst + 60, # to warm and dim earlier
        "srt_adjust": lambda srt : srt - 60, # to bright and cool later
        "brightness_adjust": lambda b,t : int(max_b * pow(b / max_b,2) * min(pow(t/5300,1.5),1)),
        "temp_adjust": lambda t : max(t - 200,min_temp),
        "on_adjust": lambda b : False if b < 10 else True
    },
    "Ceiling S":{
        "room":"Living Room",
        "sst_adjust": lambda sst : sst + 60, # to warm and dim earlier
        "srt_adjust": lambda srt : srt - 60, # to bright and cool later
        "brightness_adjust": lambda b,t : int(max_b * pow(b / max_b,2) * min(pow(t/5300,1.5),1)),
        "temp_adjust": lambda t : max(t - 200,min_temp),
        "on_adjust": lambda b : False if b < 10 else True
    },

    "Bathroom L":{
        "room":"Bathroom"
    }

}
