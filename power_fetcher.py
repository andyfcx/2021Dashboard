from requests_html import HTMLSession
import requests
import json
from utils import gsutil_upload
import os

file_name = "power.json"
base_dir = os.path.dirname(os.path.abspath(__file__))+'/'
monthly_peak = "https://raw.githubusercontent.com/readr-media/readr-data/master/electric-power/monthly_peak.csv"

def power_data_fetcher():
    # generated
    r = requests.get("http://data.taipower.com.tw/opendata01/apply/file/d006001/001.txt")
    r.content.decode('utf-8')
    gen = json.loads(r.content.decode('utf-8'))
    gg = []
    for item in gen['aaData']:
        if not item[3].endswith('%)') and item[3]!='N/A':
            try:
                c = float(item[3])
                gg.append(c)
            except ValueError:
                continue
    generated = round(sum(gg)/10, 2) # Unit in 10kW
    update_time = gen['']

    #consumed
    session = HTMLSession()
    r = session.get("https://www.taipower.com.tw/d006/loadGraph/loadGraph/load_briefing3.html") # yearly
    r.html.render()
    c = r.html.xpath('//*[@id="latest_load"]/text()')[0] # string
    consumed = round(float(c.replace(',','')), 2)
    supply_status = r.html.xpath('//*[@id="lighttext"]/text()')[0]

    m = r.html.xpath('//*[@id="supply_arranged_max"]/text()')[0]
    max_supply = float(m.replace(',',''))

    # File I/O 
    with open(base_dir + file_name) as f:
        data = json.loads(f .read())
        data.append({"time": update_time, "status": {"最大供電": max_supply, "用電": consumed, "供電狀況":supply_status}})
    with open(base_dir + file_name,'w') as f:
        f.write(json.dumps(data, ensure_ascii=False).encode('utf8').decode())

    gsutil_upload(f'{base_dir}{file_name}')
    # return generated, consumed, update_time

if __name__ == "__main__":
    power_data_fetcher()