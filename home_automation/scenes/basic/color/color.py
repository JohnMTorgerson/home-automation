import logging
import json
from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError
import os
# print(os.getcwd())
import inspect

# actual path of the script's directory, regardless of where it's being called from
path_ = os.path.dirname(inspect.getabsfile(inspect.currentframe()))

# create logger
color_logger = logging.getLogger(f"HA.{__name__}")
settings = {}

def run(client=None,bulbs=[],bulb_props={},log=True) :
    # if log=False is passed, we don't want to do any logging, so set to a null handler
    if log == False :
        # set color_logger to null handler
        global color_logger
        color_logger = logging.getLogger("null")
    else :
        # otherwise, we have to reset to the actual logger (in case False was passed previously)
        # this is clearly not the best way to handle this, but it'll work for now
        # probably this whole project needs to be re-written using classes
        color_logger = logging.getLogger(f"HA.{__name__}")


    color_logger.info("========== RUNNING COLOR SCENE ==========")

    global settings
    settings = get_user_settings()

    # bulbs = settings["bulbs"]
    # bulb_props = settings["bulb_props"]

    # color_logger.info('Running color scene...')

    if len(bulbs) > 0 and client is None or isinstance(client,list) :
        err = 'Color.run() could not get Wyze client; aborting'
        color_logger.critical(err)
        raise Exception(err)
        # pass

    # just to prettify the logging
    max_name_length = 0
    for bulb in bulbs :
        name_length = len(bulb.nickname)
        if name_length > max_name_length :
            max_name_length = name_length



    # ============ set the bulb values if the scene is on ================ #
    if settings["on"] == True :

        for bulb in bulbs:

            color = get_color(bulb.nickname)
            brightness = get_brightness(bulb.nickname)

            # GET ADJUSTED COLOR
            try:
                adjusted_color = bulb_props.bulbs[bulb.nickname]["color_adjust"](color)
            except:
                color_logger.warning(f"Could not find adjusted color for {bulb.nickname}")
                adjusted_color = color

            # GET ADJUSTED BRIGHTNESS
            try:
                adjusted_brightness = bulb_props.bulbs[bulb.nickname]["brightness_adjust"](brightness)
            except:
                color_logger.warning(f"Could not find adjusted brightness for {bulb.nickname}")
                adjusted_brightness = brightness

            # GET ON/OFF ADJUSTMENT
            try:
                turn_on = bulb_props.bulbs[bulb.nickname]["on_adjust"](adjusted_brightness)
            except:
                # color_logger.debug(f"Could not find on_adjust from bulb_props for {bulb.nickname}, so leaving on")
                turn_on = True                

            # round the brightness value to nearest integer before sending to API
            adjusted_brightness = round(adjusted_brightness)

            # color_logger.debug(f"{bulb.nickname}: temp={adjusted_temp}, brightness={adjusted_brightness}, on={turn_on}")

            # SEE IF BULB IS ACTUALLY ON OR OFF ALREADY
            try:
                is_on = client.bulbs.info(device_mac=bulb.mac).is_on
            except:
                color_logger.warning(f"Could not find on/off state for {bulb.nickname}")
                is_on = False

            # SET ALL THE VALUES WE JUST GOT
            if turn_on is True:
                # if turn_on is true, any adjustments we make will turn the bulb on if it's off,
                # so all we need to do is make the adjustments
                # color_logger.debug('on is True')
                # client.bulbs.turn_on(device_mac=bulb.mac, device_model=bulb.product.model)
                client.bulbs.set_color(device_mac=bulb.mac, device_model=bulb.product.model, color=adjusted_color)
                client.bulbs.set_brightness(device_mac=bulb.mac, device_model=bulb.product.model, brightness=adjusted_brightness)

            elif turn_on is False and is_on:
                # if turn_on is false and the bulb is actually on, then we need to manually turn it off
                # color_logger.debug('on is False and bulb.is_on')
                client.bulbs.turn_off(device_mac=bulb.mac, device_model=bulb.product.model)
                color_logger.debug(f"on_adjust for {bulb.nickname} is FALSE, so turning off")

            # just to prettify the logging
            num_spaces = max_name_length - len(bulb.nickname)
            spaces = " " * num_spaces

            color_logger.info(f"{bulb.nickname}{spaces} === color:#{adjusted_color}, brightness:{adjusted_brightness: <{3}}")#, turn_on={turn_on}, is_on={is_on}")
            # bulb_info = client.bulbs.info(device_mac=bulb.mac)
            # color_logger.debug(f"{bulb.nickname}{spaces}--- real:  {bulb_info.color},       real: {bulb_info.brightness}")

    else:
        color_logger.info(f"***************** COLOR SCENE IS SET TO OFF, NOT ADJUSTING BULBS")


def get_user_settings() :
    try:
        with open(f"{path_}/settings.json", "r") as f :
            settings = json.load(f)
    except Exception as e:
        color_logger.error(f"Error: Unable to retrieve color settings from file. Temporarily using defaults\n{e}")
        # default values
        settings = {
            "on" : False,
            "color" : "00ffff",
            "brightness" : 100,
            # "wyze_login" : {}
        }

    color_logger.info(f"Color settings: {settings}")

    return settings

# def update_settings(bulbs, bulb_props, email, password) :
#     try:
#         with open(f"{path_}/settings.json", "r+") as f :
#             settings = json.load(f)

#             settings["bulbs"] = bulbs
#             settings["bulb_props"] = bulb_props
#             settings["wyze_login"]["email"] = email
#             settings["wyze_login"]["password"] = password

#             # delete file contents
#             f.seek(0)
#             f.truncate()

#             # write updated data to file
#             json.dump(settings, f)
#             color_logger.debug('successfully updated bulb settings in settings.json')


#     except Exception as e:
#         color_logger.error(f"Error: Unable to retrieve color settings from file. Cannot update bulbs/bulb_props/login info\n{e}")

def get_color(nickname) :
    return settings["color"]

def get_brightness(nickname) :
    return settings["brightness"]

def set_values(color,brightness) :
    if color is None and brightness is None :
        return

    try:
        with open(f"{path_}/settings.json", "r+") as f :
            settings = json.load(f)

            if color is not None :
                settings["color"] = color

                # for logging
                c_str = f'color to {color}'

            if brightness is not None :
                settings["brightness"] = brightness

                # for logging
                b_str = f' brightness to {brightness}'
                if c_str :
                    b_str = f' and{b_str}'

            # delete file contents
            f.seek(0)
            f.truncate()

            # write updated data to file
            json.dump(settings, f)
            color_logger.debug(f'successfully set {c_str}{b_str} in settings.json')


    except Exception as e:
        color_logger.error(f"Error: Unable to retrieve color settings from file. Cannot update bulbs/bulb_props/login info\n{e}")

if __name__ == "__main__" :
    run()
