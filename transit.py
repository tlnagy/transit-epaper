import sys
import os
import requests
import json
import logging

args = sys.argv

logging.basicConfig(level=logging.INFO)

logging.info("Called with arguments {}".format(args))
if len(args) < 2 or args[1] != 'update':
    if not os.path.isfile("upcoming.json"):
        logging.info("No update flag and no upcoming.json, aborting...")
        exit()

# path to ePaper library
filedir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(filedir, 'e-Paper', 'RaspberryPi_JetsonNano', 'python', 'lib')

if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd4in26
import time
from PIL import Image, ImageDraw, ImageFont

# CONSTANTS
PULL_FREQ_S = 180



try:
    logging.info("Real-time Transit Output")

    epd = epd4in26.EPD()
    logging.info("Initialize display")
    epd.init_Fast()

    if len(args) < 2 or args[1] != 'update':
        logging.info("No update flag passed")

        d = {}
        with open("upcoming.json") as f:
            d = json.load(f)
        
        logging.info("Checking if upcoming file is stale")
        delta = time.time() - d['update_time']

        if delta > PULL_FREQ_S + 120:
            logging.info("Stale upcoming.json detected, clearing screen")
            bigfont = ImageFont.truetype(os.path.join(filedir, 'NotoSans.ttf'), 90)
            img = Image.new('1', (epd.width, epd.height), 255)
            draw = ImageDraw.Draw(img)

            bus = Image.open('bus.png')

            img.paste(bus, (300,150))
            epd.display_Fast(epd.getbuffer(img))
            logging.info("Removing stale upcoming.json")
            os.remove("upcoming.json")
        logging.info("Sleeping")
        epd.sleep()
        exit()

    logging.info("Loading last update")
    d = {'update_time' : 0}

    if os.path.isfile("upcoming.json"):
        with open("upcoming.json") as f:
            d = json.load(f)

    if time.time() - d['update_time'] > PULL_FREQ_S:
        logging.info("Data is stale, pulling fresh")

        url = 'https://external.transitapp.com/v3/public/stop_departures'
        headers = {'Accept': 'application/json', 'Accept-Language': 'en', 'apiKey' : os.environ["TRANSIT_APIKEY"]}

        params = {
            'global_stop_id' : 'BBB:7194'
        }
        logging.info("Requesting data from Transit API")
        req = requests.get(url, headers=headers, params=params)
        req.raise_for_status()
        logging.info("Returned {}".format(req))

        d = json.loads(req.content)
        d['update_time'] = time.time()

        with open("upcoming.json", "w") as file:
            json.dump(d, file, indent = 4)

    departures = []
    for bus in d['route_departures'][0]['itineraries'][0]['schedule_items']:
        departures.append(int((bus['departure_time'] - int(time.time())) / 60))

    logging.info("Drawing")    
    # font24 = ImageFont.truetype(, 24)
    smfont = ImageFont.truetype(os.path.join(filedir, 'NotoSans.ttf'), 40)
    medfont = ImageFont.truetype(os.path.join(filedir, 'NotoSans.ttf'), 60)
    bigfont = ImageFont.truetype(os.path.join(filedir, 'NotoSans.ttf'), 90)
    biglyfont = ImageFont.truetype(os.path.join(filedir, 'NotoSans.ttf'), 150)
    biggestfont = ImageFont.truetype(os.path.join(filedir, 'NotoSans.ttf'), 220)

    img = Image.new('1', (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(img)

    bus = Image.open('bus.png')
    W,H = 200, 120

    img.paste(bus, (0,0))
    # draw.ellipse((0, 0, 200, 200), fill=0, outline=0)
    message = "17"
    _, _, w, h = draw.textbbox((0, 0), message, font=bigfont, align="center")
    draw.text(((W - w)/2, (H - h)/2), message, font = bigfont, fill = 0, stroke_width = 2, stroke_fill = 0)
    draw.text((250,50), "Sawtelle @\nNebraska", font = smfont, fill = 0, stroke_width = 2, stroke_fill = 0)
    message = time.strftime('%H:%M')
    _, _, w, h = draw.textbbox((0, 0), message, font=bigfont, align="right", stroke_width = 2)
    draw.text((epd.width - w - 20, 10), message, font = bigfont, fill = 0, stroke_width = 2, stroke_fill = 0)

    x = -2
    y = 190
    pad = 35
    first = "{}".format(departures[0])
    _, _, w1, h1 = draw.textbbox((0, 0), first, font=biggestfont, align="left", stroke_width = 4)
    draw.text((x, y), first, font = biggestfont, fill = 0, stroke_width = 4, stroke_fill = 0)

    message = "min"
    _, _, w2, h2 = draw.textbbox((0, 0), message, font=medfont, align="left", stroke_width = 4)
    w2 = w2 - 7
    draw.text((x + w1 - 7, y + (h1 - h2)), message, font = medfont, fill = 0, stroke_width = 4, stroke_fill = 0)

    second = "{}".format(departures[1])
    _, _, w3, h3 = draw.textbbox((0, 0), second, font=biglyfont, align="left", stroke_width = 4)
    draw.text((x + w1 + w2 + pad, y + (h1 - h3)), second, font = biglyfont, fill = 0, stroke_width = 4, stroke_fill = 0)

    third = "{}".format(departures[2])
    draw.text((x + w1 + w2 + pad + w3 + pad, y + (h1 - h3)), third, font = biglyfont, fill = 0, stroke_width = 4, stroke_fill = 0)

    epd.display_Fast(epd.getbuffer(img))
    
    logging.info("Sleeping")
    epd.sleep()

except requests.exceptions.RequestException as e:
    logging.info(e)

    bigfont = ImageFont.truetype(os.path.join(filedir, 'NotoSans.ttf'), 90)
    img = Image.new('1', (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(img)

    bus = Image.open('bus.png')

    img.paste(bus, (100,150))
    if isinstance(e, requests.HTTPError):
        draw.text((320, 200), "{} error".format(e.response.status_code), font = bigfont, fill = 0, stroke_width = 2, stroke_fill = 0)
    else:
        draw.text((320, 200), "{} error".format(repr(e)), font = bigfont, fill = 0, stroke_width = 2, stroke_fill = 0)
    epd.display_Fast(epd.getbuffer(img))

    
    logging.info("Sleeping")
    epd.sleep()
    exit()