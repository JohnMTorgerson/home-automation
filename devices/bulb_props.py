bulbs = {
    "Globe":{
        "room":"Living Room",
        "brightness_adjust": lambda b : int(b/4),
        "temp_adjust": lambda t : t - 100
    },
    "Floor Lamp":{
        "room":"Living Room",
        "brightness_adjust": lambda b : b,
        "temp_adjust": lambda t : t
    },
    "Wood Lamp":{
        "room":"Living Room",
        "brightness_adjust": lambda b : b,
        "temp_adjust": lambda t : t + 100
    },
    "Left Window":{
        "room":"Living Room",
        "brightness_adjust": lambda b : b,
        "temp_adjust": lambda t : t + 250
    },
    "Right Window":{
        "room":"Living Room",
        "brightness_adjust": lambda b : b,
        "temp_adjust": lambda t : t + 250
    }
}
