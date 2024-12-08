import datetime


def info(string, end='\n'):
    print(f'[{datetime.datetime.now()}] {string}', end=end)