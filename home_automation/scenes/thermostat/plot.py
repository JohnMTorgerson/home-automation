from matplotlib import pyplot as plt
import json
from datetime import datetime
import re
from pprint import pprint

def main() :
    # plot weather data
    weather_filepath = "../data/weather_data.json"
    data = get_weather_data(weather_filepath)
    # plot(data)

    # plot indoor temperature data
    temp_filepath = "../data/data.txt"
    data = get_temp_data(temp_filepath)
    plot(data)


# get weather data
def get_weather_data(filepath) :
    # first open existing file and get old data
    try:
        with open(filepath,'r') as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError as e:
                print(f'Error loading data from {filepath}: {e}')

                if not f.read(1):
                    print('File exists but is empty')
                    data = {}
                else:
                    raise e

    except FileNotFoundError as e:
        print("No existing data file found")
        data = {}

    return data

def get_temp_data(filepath) :
    data = {}

    # open file and format data
    try:
        with open(filepath,'r') as f:
            for line in f :
                line_data = line.split()
                try :
                    key = int(line_data[0])
                except Exception as e:
                    print(f'Unable to parse timestamp in line (skipping): {line} -- {e}')
                    continue

                try :
                    data[key] = {
                        "temp" : float(line_data[1]),
                        "humidity" : float(line_data[2])
                    }
                except IndexError as e:
                    print(f'Unable to parse line (skipping): {line} -- {e}')
                except ValueError as e:
                    print(f'Unable to parse temp/humidity in line, assuming it contains a non-datapoint label: {line}')

                    match = re.search(r"\[.*\]", line)
                    result = match.group()
                    if (result) :
                        data[key] = {
                            "label" : result
                        }

    except FileNotFoundError as e:
        print("No existing data file found")

    pprint(data)

    return data


def plot(data) :
    x_data = []
    y_data = []
    for key in data :
        x_data.append(datetime.fromtimestamp(int(key)))
        try :
            y_data.append(float(data[key]["Temperature (degrees F)"]))
        except KeyError as e:
            try:
                y_data.append(float(data[key]["temp"]))
            except KeyError as e:
                y_data.append(data[key]["label"])




    list=zip(*sorted(zip(*(x_data,y_data))))
    plt.plot(*list)


    # plt.plot(x_data,y_data)
    plt.gcf().autofmt_xdate()
    plt.xlabel("Time")
    plt.ylabel("Temp (F)")
    plt.show()

if __name__ == "__main__" :
    main()
