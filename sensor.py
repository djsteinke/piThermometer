import smbus
import time
import datetime as dt


bus = smbus.SMBus(1)
config = [0x08, 0x00]
check_interval = 60
next_check = dt.datetime.utcnow()
next_check = next_check.replace(tzinfo=dt.timezone.utc)

c = 0
f = 0
h = 0


def get_f_from_c():
    return c*1.8+32


def get_sensor_temp():
    try:
        bus.write_i2c_block_data(0x38, 0xE1, config)
        byt = bus.read_byte(0x38)
        measure_cmd = [0x33, 0x00]
        bus.write_i2c_block_data(0x38, 0xAC, measure_cmd)
        time.sleep(0.5)
        data = bus.read_i2c_block_data(0x38, 0x00)
        temp_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
        temp_c = ((temp_raw*200) / 1048576) - 50
        humid_raw = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
        humid = humid_raw * 100 / 1048576
        return [round(temp_c, 2), round(humid, 1)]
    except:
        return [0, -1]


def check_sensor(now):
    global next_check, c, h, f
    if next_check < now:
        c, h = get_sensor_temp()
        f = get_f_from_c()
        c = round(c, 1)
        f = round(f, 1)
        next_check += dt.timedelta(seconds=check_interval)
    return {"c": c, "f": f, "h": h}
