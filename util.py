from datetime import datetime
import json
import threading


# read json file with the S&P500
def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)

    return sp500_json["sp500"]

# append a string to a log file
def write_to_log(path, text):    
    with open(path, "a") as log:
        log.write(str(datetime.now()) + " " + text.replace("\n", " ") + "\n")

    return


# append a string to a log file
def write_to_log_with_lock(path, text, lock):
    lock.acquire()

    with open(path, "a") as log:
        log.write(str(datetime.now()) + " " + text.replace("\n", " ") + "\n")

    lock.release()
    return
