import csv
import time
import serial
import re

'''Specify the port'''
ser = serial.Serial("/dev/tty.SLAB_USBtoUART", 115200, timeout=True)

column_name = ["elapsed_time", "peltier_temp", "touch_value", "touch_judgment"]
csv_data = [column_name]
start_time = time.time()


def create_csv(data_list):
    for data in data_list:
        with open("./esp_serial_data/sample.csv", mode="a") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(data)
    return


def create_data(serial_data):
    num_extraction_lis = re.findall(r'\d[.]\d\d|\d\d[.]\d\d|\d\d\d[.]\d\d|\d\d|\d|false|true', serial_data)
    if len(num_extraction_lis) == 3:
        current_time = time.time()
        elapsed_time = round(current_time - start_time, 2)
        peltier_temp = num_extraction_lis[0]
        touch_value = num_extraction_lis[1]
        touch_judgment = num_extraction_lis[2]
        return elapsed_time, peltier_temp, touch_value, touch_judgment
    else:
        return


'''Get and display serial data.Save data csv with ctrl + c'''
try:
    while True:
        line = ser.readline().rstrip().decode("utf-8")
        serial_data = create_data(line)
        if serial_data:
            print(serial_data)
            csv_data.append([serial_data[0], serial_data[1], serial_data[2], serial_data[3]])
        else:
            continue

except KeyboardInterrupt:
    if len(csv_data) < 10000:
        create_csv(csv_data)
        print("FINISH")
    else:
        print("Data is large")
