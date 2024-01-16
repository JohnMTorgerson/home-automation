import math
r = 8.314462 # molar gas constant (m^3⋅Pa⋅K^−1⋅mol^−1 or kg⋅m^2⋅s^−2⋅K^−1⋅mol^−1 or J⋅K^−1⋅mol^−1)
m = 18.01528 # molar mass of water (grams/mole)


def main() :
    while True :
        temp_f = input("Temp (F):")
        rel_hum = input("Relative Humidity:")
        temp_c = (float(temp_f)-32) * 5/9

        ah = estimate(rel_hum,temp_c)

        volume = 110 # volume of apartment minus bedroom is roughly 110 m^3
        water_mass = ah * volume

        print(f"Temp (C): {temp_c}")
        # print(f"Vapor Pressure: {vp/1000:.2f} kPa")
        print(f"Water In Air: {water_mass:.2f} g or mL")
        print(f"Absolute Humidity: {ah:.2f} g/m^3")
        print("")

def estimate(rel_hum_pct,temp_c) :
    rel_hum_frac = float(rel_hum_pct) / 100 # convert from percentage to fraction
    vp = vapor_pressure(temp_c)
    ah = absolute_humidity(rel_hum_frac,vp,temp_c)
    return ah

def absolute_humidity(rel_hum_frac,vapor_pressure, temp_c) :
    temp_k = temp_c + 273.2

    vapor_density = (vapor_pressure * m) / (r * temp_k) 

    abs_hum = rel_hum_frac * vapor_density

    return abs_hum

def vapor_pressure(temp_c) :
    # https://en.wikipedia.org/w/index.php?title=Antoine_equation&oldid=1102656080

    # constants for Antoine equation for water, valid from 1C to 100C
    a = 8.07131 + math.log10(101325/760) # convert A from mmHg to Pa by adding constant
    b = 1730.63
    c = 233.426
    vapor_pressure = pow(10,a - b / (c + temp_c))

    return vapor_pressure

if __name__ == "__main__" :
    main()