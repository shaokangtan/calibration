from datetime import datetime


def debug(str):
    now = datetime.now()
    print(now.strftime("%m/%d/%Y, %H:%M:%S "), end="")
    print(str)
