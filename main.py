import datetime
import re
import tkinter
import urllib.request

from bs4 import BeautifulSoup


def fetch_metar():
    if len(entry_airport_icao.get()) <= 3:
        print("METAR not found")
        metar_fetched_time_label.config(text="")
        metar_result_string.config(text="METAR取得失敗（空港が存在しないか、METARが発出されていません。）")
        metar_obs_time.config(text="")
        metar_wind.config(text="")
        metar_visibility.config(text="")
        metar_altimeter.config(text="")
    else:
        url = "http://metar.vatsim.net/metar.php?id=" + entry_airport_icao.get()
        res = urllib.request.urlopen(url)
        metar_string_raw = BeautifulSoup(res, 'html.parser')
        current_time = datetime.datetime.now()
        current_time_formatted = current_time.strftime('最終取得(ローカル時間): %Y年%m月%d日 %H時%M分')
        print(current_time, metar_string_raw)
        metar_string_text = metar_string_raw.get_text()
        metar_fetched_time_label.config(text=current_time_formatted)
        metar_result_string.config(text=metar_string_text, fg="blue")
        root.after(300000, fetch_metar)
        metar_find_obs_time(metar_string_text.split())
        metar_find_wind(metar_string_text.split())
        metar_find_visibility(metar_string_text.split())
        metar_find_temp_dewpoint(metar_string_text)
        metar_find_altimeter(metar_string_text)
        
def metar_find_obs_time(list_metar):
    metar_obs_time_raw = list_metar[1] #オブザベーション日時のみ取得
    obs_day = metar_obs_time_raw[0:2] #オブザベーション日のみ取得
    obs_time_hour = metar_obs_time_raw[2:4] #オブザベーション時間のみ取得
    obs_time_minute = metar_obs_time_raw[4:6] #オブザベーション分のみ取得
    metar_obs_time.config(text="発出時間(UTC): " + obs_day + "日" + obs_time_hour + "時" + obs_time_minute + "分")

def metar_find_wind(list_metar):
    if list_metar[2] == "AUTO":
        metar_wind_raw = list_metar[3]
    else:
        metar_wind_raw = list_metar[2]
    
    wind_direction = metar_wind_raw[0:3]
    wind_speed = metar_wind_raw[3:5]
    if metar_wind_raw[7:] == "":
        metar_wind.config(text="風量と風速: " + wind_direction + "@" + wind_speed + "KT")
    else:
        wind_gust = metar_wind_raw[6:8]
        metar_wind.config(text="風量と風速: " + wind_direction + "@" + wind_speed + "KT" + wind_gust + "G")
        

def metar_find_visibility(list_metar):
    if list_metar[2] == "AUTO":
        metar_visibility_find = list_metar[4]
        if "V" in metar_visibility_find:
            if list_metar[5] == "CAVOK":
                metar_visibility_raw = "9999"
            else:
                metar_visibility_raw = list_metar[5]
        else:
            if list_metar[4] == "CAVOK":
                metar_visibility_raw = "9999"
            else:
                metar_visibility_raw = list_metar[4]
    else:
        metar_visibility_find = list_metar[3]
        if "V" in metar_visibility_find:
            if list_metar[4] == "CAVOK":
                metar_visibility_raw = "9999"
            else:
                metar_visibility_raw = list_metar[4]
        else:
            if list_metar[3] == "CAVOK":
                metar_visibility_raw = "9999"
            else:
                metar_visibility_raw = list_metar[3]
    
    print(metar_visibility_raw)
    if metar_visibility_raw == "9999":
        metar_visibility.config(text="地上視程: 10km以上")
    else:
        metar_visibility.config(text="地上視程(m): " + metar_visibility_raw)

def metar_find_temp_dewpoint(metar_string_text):
    if re.search(r'([0-9]{2}/[0-9]{,3})', metar_string_text):
        res = re.search(r'([0-9]{2}/[0-9]{,3})', metar_string_text)
        temp = res.group()[:2]
        dewpoint = res.group()[3:]
        metar_temp.config(text="気温: " + temp + "C")
        metar_dewpoint.config(text="露点: " + dewpoint + "C")

def metar_find_altimeter(metar_string_text):
    if re.search(r'A([0-9]{4})', metar_string_text):
        res = re.search(r'A([0-9]{4})', metar_string_text)
        QNH_raw = res.group()[1:]
        QNH_first = QNH_raw[:2]
        QNH_last = QNH_raw[2:]
        QNH = QNH_first + "." + QNH_last
        metar_altimeter.config(text="QNH: " + QNH)
    else:
        res = re.search(r'Q([0-9]{4})', metar_string_text)
        hPa = res.group()[1:]
        
        with open("hPa_inHg.txt", "r") as f:
            lines = f.read().splitlines()
        
        for line in lines:
            if hPa in line:
                QNH = line[5:]
                metar_altimeter.config(text="QNH: " + QNH)
        

root = tkinter.Tk()
root.title("VATSIM Metar Fetcher")
root.geometry("500x300")
entry_airport_label = tkinter.Label(root, text="ICAOコード")
entry_airport_label.pack()
entry_airport_label_fyi = tkinter.Label(root, text="（北アメリカのMETARは正常に表示されない可能性あり）")
entry_airport_label_fyi.pack()
entry_airport_icao = tkinter.Entry(root)
entry_airport_icao.pack()
metar_fetch_button = tkinter.Button(root, text="METARを今すぐ取得", command=fetch_metar)
metar_fetch_button.pack()
metar_fetched_time_label = tkinter.Label(root, justify="left")
metar_fetched_time_label.pack()
metar_result_string = tkinter.Label(root, justify="left", wraplength=500)
metar_result_string.pack()
metar_obs_time = tkinter.Label(root, justify="left")
metar_obs_time.pack()
metar_wind = tkinter.Label(root, justify="left")
metar_wind.pack()
metar_visibility = tkinter.Label(root, justify="left")
metar_visibility.pack()
metar_temp = tkinter.Label(root, justify="left")
metar_temp.pack()
metar_dewpoint = tkinter.Label(root, justify="left")
metar_dewpoint.pack()
metar_altimeter = tkinter.Label(root, justify="left")
metar_altimeter.pack()
root.mainloop()