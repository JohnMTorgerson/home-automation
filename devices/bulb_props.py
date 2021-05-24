min_temp = 1800
max_temp = 6500

bulbs = {
    "Globe":{
        "room":"Living Room",
        "brightness_adjust": lambda b : int(b/4),
        "temp_adjust": lambda t : max(t - 100,min_temp)
    },
    "Floor Lamp":{
        "room":"Living Room",
        "brightness_adjust": lambda b : b,
        "temp_adjust": lambda t : t
    },
    "Wood Lamp":{
        "room":"Living Room",
        "brightness_adjust": lambda b : b,
        "temp_adjust": lambda t : min(t + 100,max_temp)
    },
    "Left Window":{
        "room":"Living Room",
        "brightness_adjust": lambda b : b,
        "temp_adjust": lambda t : min(t + 250,max_temp)
    },
    "Right Window":{
        "room":"Living Room",
        "brightness_adjust": lambda b : b,
        "temp_adjust": lambda t : min(t + 250,max_temp)
    }
}
