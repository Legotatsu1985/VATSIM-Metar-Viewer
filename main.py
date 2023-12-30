import datetime
import re
import tkinter
import urllib.request

from bs4 import BeautifulSoup


def fetch_metar():
    if len(entry_airport_icao.get()) <= 3: #入力したICAOコードが3桁以下の場合（ICAOコードを読み込めない）
        print("METAR not found")
        metar_fetched_time_label.config(text="")
        metar_result_string.config(text="METAR取得失敗（空港が存在しないか、METARが発出されていません。）", fg="red")
        metar_obs_time.config(text="")
        metar_wind.config(text="")
        metar_visibility.config(text="")
        metar_temp.config(text="")
        metar_dewpoint.config(text="")
        metar_altimetar_hPa.config(text="")
        metar_altimeter_inHg.config(text="")
    else: #ICAOコードが4桁である
        url = "http://metar.vatsim.net/metar.php?id=" + entry_airport_icao.get() #VATSIMメータphpリンクとICAOコードを加算
        res = urllib.request.urlopen(url) #URLを検索
        metar_string_raw = BeautifulSoup(res, 'html.parser') #VATSIMメータphpよりメーターテキストを採取
        current_time = datetime.datetime.now() #現在時刻を取得
        current_time_formatted = current_time.strftime('%Y年%m月%d日 %H時%M分')
        print(current_time, metar_string_raw)
        metar_string_text = metar_string_raw.get_text()
        metar_fetched_time_label.config(text=current_time_formatted)
        metar_result_string.config(text=metar_string_text, fg="blue")
        root.after(300000, fetch_metar)
        list_metar = metar_string_text.split()
        metar_find_obs_time(list_metar)
        metar_find_wind(list_metar)
        metar_find_visibility(list_metar)
        metar_find_temp_dewpoint(metar_string_text)
        metar_find_altimeter_hPa(metar_string_text)
        metar_find_altimeter_inHg(metar_string_text)
        
def metar_find_obs_time(list_metar):
    metar_obs_time_raw = list_metar[1] #オブザベーション日時のみ取得
    obs_day = metar_obs_time_raw[0:2] #オブザベーション日のみ取得
    obs_time_hour = metar_obs_time_raw[2:4] #オブザベーション時間のみ取得
    obs_time_minute = metar_obs_time_raw[4:6] #オブザベーション分のみ取得
    metar_obs_time.config(text=obs_day + "日" + obs_time_hour + "時" + obs_time_minute + "分")

def metar_find_wind(list_metar):
    if list_metar[2] == "AUTO":
        metar_wind_raw = list_metar[3]
    else:
        metar_wind_raw = list_metar[2]
    
    wind_direction = metar_wind_raw[0:3]
    wind_speed = metar_wind_raw[3:5]
    if metar_wind_raw[7:] == "":
        metar_wind.config(text=wind_direction + "@" + wind_speed + "KT")
    else:
        wind_gust = metar_wind_raw[6:8]
        metar_wind.config(text=wind_direction + "@" + wind_speed + "G" + wind_gust + "KT")
        

def metar_find_visibility(list_metar):
    if list_metar[2] == "AUTO":
        metar_visibility_find = list_metar[4]
        if re.search(r'([0-9]{3}V[0-9]{3})', metar_visibility_find):
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
        if re.search(r'([0-9]{3}V[0-9]{3})', metar_visibility_find):
            if list_metar[4] == "CAVOK":
                metar_visibility_raw = "9999"
            else:
                metar_visibility_raw = list_metar[4]
        else:
            if list_metar[3] == "CAVOK":
                metar_visibility_raw = "9999"
            else:
                metar_visibility_raw = list_metar[3]
    
    if metar_visibility_raw == "9999":
        metar_visibility.config(text="10km以上")
    else:
        metar_visibility.config(text=metar_visibility_raw + "m")

def metar_find_temp_dewpoint(metar_string_text):
    temp_dewpoint_combo_MM = r'(M[0-9]{2}/M[0-9]{,3})'
    temp_dewpoint_combo_MP = r'(M[0-9]{2}/[0-9]{,3})'
    temp_dewpoint_combo_PM = r'([0-9]{2}/M[0-9]{,3})'
    temp_dewpoint_combo_PP = r'([0-9]{2}/[0-9]{,3})'
    if re.search(temp_dewpoint_combo_MM, metar_string_text):
        res = re.search(temp_dewpoint_combo_MM, metar_string_text)
        temp_minus = "-" + res.group()[1:3]
        dewpoint_minus = "-" + res.group()[5:]
        metar_temp.config(text=temp_minus)
        metar_dewpoint.config(text=dewpoint_minus)
    elif re.search(temp_dewpoint_combo_MP, metar_string_text):
        res = re.search(temp_dewpoint_combo_MP, metar_string_text)
        temp_minus = "-" + res.group()[1:3]
        dewpoint_plus = res.group()[4:]
        metar_temp.config(text=temp_minus)
        metar_dewpoint.config(text=dewpoint_plus)
    elif re.search(temp_dewpoint_combo_PM, metar_string_text):
        res = re.search(temp_dewpoint_combo_PM, metar_string_text)
        temp_plus = res.group()[:2]
        dewpoint_minus = "-" + res.group()[4:]
        metar_temp.config(text=temp_plus)
        metar_dewpoint.config(text=dewpoint_minus)
    else:
        res = re.search(temp_dewpoint_combo_PP, metar_string_text)
        temp_plus = res.group()[:2]
        dewpoint_plus = res.group()[3:]
        metar_temp.config(text=temp_plus)
        metar_dewpoint.config(text=dewpoint_plus)

def metar_find_altimeter_hPa(metar_string_text):
    if re.search(r'Q([0-9]{4})', metar_string_text):
        res = re.search(r'Q([0-9]{4})', metar_string_text)
        hPa = res.group()[1:]
        metar_altimetar_hPa.config(text=hPa)
    else:
        metar_altimetar_hPa.config(text="")

def metar_find_altimeter_inHg(metar_string_text):
    if re.search(r'A([0-9]{4})', metar_string_text):
        res = re.search(r'A([0-9]{4})', metar_string_text)
        QNH_raw = res.group()[1:]
        QNH_first = QNH_raw[:2]
        QNH_last = QNH_raw[2:]
        QNH = QNH_first + "." + QNH_last
        metar_altimeter_inHg.config(text=QNH)
    else:
        res = re.search(r'Q([0-9]{4})', metar_string_text)
        hPa = res.group()[1:]
        
        with open("hPa_inHg.txt", "r") as f:
            lines = f.read().splitlines()
        
        for line in lines:
            if hPa in line:
                QNH = line[5:]
                metar_altimeter_inHg.config(text=QNH)



root = tkinter.Tk()
root.title("VATSIM Metar Fetcher")
root.geometry("500x350")
entry_airport_label = tkinter.Label(root, text="ICAOコードを入力→")
entry_airport_icao = tkinter.Entry(root, width=10)
metar_fetch_button = tkinter.Button(root, text="METARを今すぐ取得", command=fetch_metar)
metar_fetchstop_button = tkinter.Button(root, text="自動取得停止")
metar_fetched_time_label_fixed_text = tkinter.Label(root, text="最終取得(ローカル時間):", justify="left")
metar_fetched_time_label = tkinter.Label(root, justify="left")
metar_result_string = tkinter.Label(root, justify="left", wraplength=450)
metar_obs_time = tkinter.Label(root, justify="left")
metar_wind = tkinter.Label(root, justify="left")
metar_visibility = tkinter.Label(root, justify="left")
metar_temp = tkinter.Label(root, justify="left")
metar_dewpoint = tkinter.Label(root, justify="left")
metar_altimetar_hPa = tkinter.Label(root, justify="left")
metar_altimeter_inHg = tkinter.Label(root, justify="left")
info_label = tkinter.Label(root, text="Made by Legotatsu with Tkinter", fg="blue", anchor=tkinter.S)
version_label = tkinter.Label(root, text="v1.1", anchor=tkinter.SE)
entry_airport_label.grid(column=0, row=0)
entry_airport_icao.grid(column=1, row=0)
metar_fetch_button.grid(column=2, row=0)
metar_fetchstop_button.grid(column=3, row=0)
metar_fetched_time_label_fixed_text.grid(column=0, row=1, sticky=tkinter.E)
metar_fetched_time_label.grid(column=1, columnspan=2, row=1, sticky=tkinter.W)
metar_result_string.grid(column=0, columnspan=5, row=2, sticky=tkinter.W)
root.mainloop()