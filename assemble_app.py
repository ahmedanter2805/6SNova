import os
import re
from bs4 import BeautifulSoup

base_stitch = r'C:\Users\Ahmed Anter\Desktop\Nasa Space Apps\stitch_remix_of_earth_climate_satellite_monitor\stitch_remix_of_earth_climate_satellite_monitor'

def get_inner_div(folder):
    path = os.path.join(base_stitch, folder, 'code.html')
    if not os.path.exists(path):
        return ""
    soup = BeautifulSoup(open(path, encoding='utf-8').read(), 'html.parser')
    main = soup.find('main')
    if not main:
        return ""
    first_div = main.find('div')
    return "".join(str(c) for c in first_div.children)

sat_html = get_inner_div('satellite_data')
alert_html = get_inner_div('emergency_alerts')
mission_html = get_inner_div('mission_control')

# Clean up any duplicate IDs or conflicting headers if necessary
# In sat_html, alert_html, mission_html: they are inside section/div containers.
# Let's verify that fonts and styling are consistent.

# Read current observatory page from frontend/index.html
curr_index = open(r'C:\Users\Ahmed Anter\Desktop\Nasa Space Apps\frontend\index.html', encoding='utf-8').read()

# We will inject the pages inside <main>:
# <div id="page-observatory" class="page-content"> ... </div>
# <div id="page-satellite" class="page-content hidden"> sat_html </div>
# <div id="page-alerts" class="page-content hidden"> alert_html </div>
# <div id="page-mission" class="page-content hidden"> mission_html </div>

# Let's find the closing of page-observatory in curr_index:
split_marker = '</div><!-- /page-observatory -->'

if split_marker in curr_index:
    parts = curr_index.split(split_marker)
    new_html = parts[0] + '</div><!-- /page-observatory -->\n\n'
    
    new_html += '<!-- === PAGE: SATELLITE DATA === -->\n'
    new_html += '<div id="page-satellite" class="page-content hidden">\n'
    new_html += sat_html + '\n'
    new_html += '</div><!-- /page-satellite -->\n\n'

    new_html += '<!-- === PAGE: EMERGENCY ALERTS === -->\n'
    new_html += '<div id="page-alerts" class="page-content hidden">\n'
    new_html += alert_html + '\n'
    new_html += '</div><!-- /page-alerts -->\n\n'

    new_html += '<!-- === PAGE: MISSION CONTROL === -->\n'
    new_html += '<div id="page-mission" class="page-content hidden">\n'
    new_html += mission_html + '\n'
    new_html += '</div><!-- /page-mission -->\n\n'

    new_html += parts[1]

    with open(r'C:\Users\Ahmed Anter\Desktop\Nasa Space Apps\frontend\index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Successfully assembled full index.html! New length:", len(new_html))
else:
    print("Split marker not found!")
