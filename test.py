import urllib.request
from time import sleep

import schedule
from bs4 import BeautifulSoup

with open("hPa_inHg.txt", "r") as f:
    lines = f.read().splitlines()

for line in lines:
    if "1013" in line:
        QNH = line[5:]
        print(QNH)