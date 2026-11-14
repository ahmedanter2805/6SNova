import os
import re
from bs4 import BeautifulSoup

base = r'C:\Users\Ahmed Anter\Desktop\Nasa Space Apps\stitch_remix_of_earth_climate_satellite_monitor\stitch_remix_of_earth_climate_satellite_monitor'

def get_inner_div(folder):
    path = os.path.join(base, folder, 'code.html')
    if not os.path.exists(path):
        return ""
    soup = BeautifulSoup(open(path, encoding='utf-8').read(), 'html.parser')
    main = soup.find('main')
    if not main:
        return ""
    first_div = main.find('div')
    # Return inner children as html string
    return "".join(str(c) for c in first_div.children)

sat_html = get_inner_div('satellite_data')
alert_html = get_inner_div('emergency_alerts')
mission_html = get_inner_div('mission_control')

print("Satellite HTML length:", len(sat_html))
print("Alert HTML length:", len(alert_html))
print("Mission HTML length:", len(mission_html))
