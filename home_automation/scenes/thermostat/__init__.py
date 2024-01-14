import os
import inspect

# actual path of the script's directory, regardless of where it's being called from
path_ = os.path.dirname(inspect.getabsfile(inspect.currentframe()))

settings_filepath = f"{path_}/settings.json"
weather_data_filepath = f"{path_}/data/weather_data.json"
therm_data_filepath = f"{path_}/data/data.txt"
