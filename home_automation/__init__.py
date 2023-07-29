# from home_automation.scenes.timebased.sunlight import sunlight as sunlight_scene
# from home_automation.scenes.basic.color import color as color_scene
# from home_automation.scenes.basic.thermostat import thermostat as thermostat_scene

from home_automation import sunlight_scene
from home_automation import color_scene
# from home_automation import wakeup
from home_automation import thermostat_scene

__all__ = [
    'sunlight_scene',
    'color_scene',
    # 'wakeup_scene',
    'thermostat_scene'
]
