"""
PyPortal AQI
"""

import time
import json
import board
import displayio
import neopixel
from adafruit_pyportal import PyPortal
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font

try:
    from secrets import secrets
except ImportError:
    print("""WiFi settings are kept in secrets.py, please add them there!
the secrets dictionary must contain 'ssid' and 'password' at a minimum""")
    raise

#Enter Air Now API and your location and delay between refreshes in seconds below.  
AIRNOWAPIKEY =""
LAT = "XX.XXXX"
LON = "XX.XXXX"
refreshtime = 600
#pylint:disable=line-too-long
aqiurl ="http://www.airnowapi.org/aq/observation/latLong/current/?format=application/json&latitude="+LAT+"&longitude="+LON+"&distance=25&API_KEY="+AIRNOWAPIKEY
#pylint:enable=line-too-long

MARGIN = 10
SPACE_BETWEEN_BARS = 1

COLORS = [0x00FF00, 0x00e400, 0xffff00,
          0xff7e00, 0xff0000, 0x8f3f97,
          0x7e0023]

cwd = ("/"+__file__).rsplit('/', 1)[0]

#CAPTION_FONT_FILE = cwd+'/fonts/Helvetica-Bold-16.bdf'
CAPTION_FONT_FILE = cwd+'/fonts/HelveticaNeue-24.bdf'
#CAPTION_FONT_FILE = cws+'/Helvetica-Bold-100.bdf'
#AQI_FONT_FILE = cwd+'/fonts/Arial-Bold-12.bdf'
AQI_FONT_FILE = cwd+'/fonts/HelveticaNeue-24.bdf'
FOOTER_FONT_FILE = cwd+'/fonts/HelveticaNeueMedium-12.bdf'

#pyportal = PyPortal(url=aqiurl,
#                    status_neopixel=board.NEOPIXEL,
#                    default_bg=0x000000,
#                    caption_font=CAPTION_FONT_FILE)

pyportal = PyPortal(url=aqiurl,
                    default_bg=0x000000,
                    caption_font=CAPTION_FONT_FILE)


canvas = displayio.Group(max_size=36)
pyportal.splash.append(canvas)
AQI_font = bitmap_font.load_font(AQI_FONT_FILE)
Footer_font = bitmap_font.load_font(FOOTER_FONT_FILE)

status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)
status_light[0] = (00, 0, 00)
#status_light[0] = (30, 00, 00, 10)

while True:
    worst = 0
    json_payload = ''
    try:
        json_payload = pyportal.fetch()
        raw_data = json.loads(json_payload)
    except (ValueError, RuntimeError) as ex:
        print('Error: ', ex)
        if isinstance(ex, ValueError):
            print('JSON:', json_payload)
        print('Retrying in 10 minutes')
        time.sleep(600)
        continue
        
    while len(canvas) > 0:
        canvas.pop()
    pyportal.set_caption(('Air Quality Index'),
                         (70, 20),
                         0xFFFFFF)
    
    xpos = 20
    ypos = 80
    print ('Name\tAQI\tCat.\tCatNum')
    for item in raw_data:
        print("{}\t{}\t{}\t{}".format(item['ParameterName'],item['AQI'],item['Category']['Name'],item['Category']['Number']))
        aqidata = str(item['ParameterName'])+': '+str(item['AQI'])+' '+str(item['Category']['Name'])
        aqicolor = (COLORS[item['Category']['Number']])
        aqi_label = Label(AQI_font, text=aqidata, color=aqicolor, x=xpos, y=ypos)
        canvas.append(aqi_label)
        ypos=ypos+40
        #get and store the highest value AQI in worst.  
        if int(item['Category']['Number']) > worst:
            worst = int(item['Category']['Number'])
    
    status_light[0] = COLORS[worst]
    print ('LED color set to ' + str(COLORS[worst]))

    footertext = "Observed in " + item['ReportingArea'] + " around " + str(item['HourObserved']) + ":00 on " + str(item['DateObserved'])
    footer_label = Label(Footer_font, text=footertext, color=0xFFFFFF, x=5, y=225)
    canvas.append(footer_label)
    
    print (footertext)
    
    # sleep awhile before re-running/refreshing.
    time.sleep(refreshtime)                  
