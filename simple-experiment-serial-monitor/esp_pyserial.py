import csv
import time

import serial
import re

'''Specify the port'''
ser = serial.Serial("/dev/tty.SLAB_USBtoUART", 115200, timeout=True)

column_name = ["elapsed_time", "peltier_temp", "touch_value", "touch_judgment"]
csv_data = [column_name]
start_time = time.time()

touch_time = None


def generate_file_name(touch_second=None) -> str:
    file_name = input("boxの色と提示した温度を入力してください(例:blue-temp40): ")
    if not file_name:
        file_name = input("boxの色と提示した温度を入力してください(例:blue-temp40): ")
    temp_subjective_evaluation = input("温度の評価を1~3で(1=冷たい,2=常温,3=温かい)行ってください: ")
    if not temp_subjective_evaluation:
        temp_subjective_evaluation = input("温度の評価を1~3で(1=冷たい,2=常温,3=温かい)行ってください: ")
    file_name = f"temp-sub-eval[{temp_subjective_evaluation}]-" + file_name
    if touch_second:
        file_name = f"experimental_data/{file_name}-touch_time-{touch_second}s.csv"
    else:
        file_name = f"experimental_data/{file_name}-touch_time_not_working.csv"
        print("touch sensorが正常に動作していません")
    return file_name


def create_csv(data_list, save_file: str):
    for data in data_list:
        with open(save_file, mode="a") as f:
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
    prev_touch_judgment = "false"
    prev_elapsed_time = 0
    while True:
        line = ser.readline().rstrip().decode("utf-8")
        serial_data = create_data(line)
        if serial_data:
            if prev_touch_judgment == "false" and serial_data[3] == "true":
                prev_elapsed_time = serial_data[0]
                prev_touch_judgment = serial_data[3]
            if prev_touch_judgment == "true" and serial_data[3] == "false":
                touch_time = round(serial_data[0] - prev_elapsed_time, 2)
                prev_touch_judgment = "false"
                print(touch_time)
            print(serial_data)
            csv_data.append([serial_data[0], serial_data[1], serial_data[2], serial_data[3]])
        else:
            continue

except KeyboardInterrupt:
    if len(csv_data) < 10000:
        create_csv(csv_data, generate_file_name(touch_time))
        print("FINISH:")
    else:
        print("Data is large")
