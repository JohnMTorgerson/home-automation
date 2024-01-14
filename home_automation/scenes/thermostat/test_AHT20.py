import time
import board
import adafruit_ahtx0

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = adafruit_ahtx0.AHTx0(i2c)

while True:
    print(f"\nTemperature: {sensor.temperature:.1f}º C")
    print(f"Temperature: {(sensor.temperature * 9/5 + 32):.1f}º F")
    print(f"Humidity: {sensor.relative_humidity:.1f}%")
    time.sleep(2)
