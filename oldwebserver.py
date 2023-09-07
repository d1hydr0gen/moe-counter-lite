# Recoding in NodeJs
import http.server
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import mimetypes
from urllib.parse import urlparse, parse_qs
import re
import threading
import time
import sqlite3
import json
import xml.etree.ElementTree as ET
import base64

# DO NOT CHANGE THIS
counters = []
themes = []
####################

# PortBind Setting
BIND = "0.0.0.0" 
PORT = 8000

# Default Theme
default_theme = "gelbooru"

# Advanced Setting
# If count is reached MAX, it will stop counting
MAX = 9999999
# Database Name ( only SQLITE3 supported for now. )
database = "database.db"
# Update Duration (seconds) for low spec machines recommend is 10, for high spec machine 1 also works
duration = 5


class Counter:
    def __init__(self, id, count):
        self.id = id
        self.count = count
        self.svg = []

class Theme:
    def __init__(self, name):
        self.name = name
        self.letters = []
class Letter:
    def __init__(self, letter,url):
        self.letter = letter
        self.url = url



def init():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS count (
            id TEXT PRIMARY KEY,
            count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    cursor.execute('SELECT * FROM count')
    records = cursor.fetchall()
    for record in records:
        counters.append(Counter(record[0],record[1]))
    conn.close()
    initTheme()

def encode_file_to_base64(file_path):
    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()
        mime_type, _ = mimetypes.guess_type(file_path)
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        return  f'data:{mime_type};base64,{encoded_content}'
    except FileNotFoundError:
        return None
    except Exception as e:
        return str(e) 



def initTheme():
    with open('themes.json', 'r') as file:
        data = json.load(file)
    for theme in data['themes']:
        theme_data = Theme(theme["name"])
        for key, value in theme['letters'].items():
            theme_data.letters.append(Letter(key,encode_file_to_base64(value)))
        themes.append(theme_data)

def create_svg(ct,theme):
    namespaces = {
        'xmlns': 'http://www.w3.org/2000/svg',
        'xmlns:xlink': 'http://www.w3.org/1999/xlink'
    }
    svg = ET.Element('svg',attrib=namespaces, width="{( len(list(str(MAX))) * 45 )}", height="100", version="1.1",
                     style="image-rendering: pixelated;")
    title = ET.SubElement(svg, 'title')
    title.text = "Moe Count"
    group = ET.SubElement(svg, 'g')

    st = str(ct)
    if len(list(st)) != len(list(str(MAX))):
        diff = len(list(str(MAX))) - len(list(st))
        for diffloop in range(diff):
            st = "0" + st
    spl = list(st)
    image_urls = []
    for l in spl:
        image_urls.append(theme.letters[int(l)].url)

    # Create image elements and set their attributes with the URLs
    for x, url in enumerate(image_urls):
        image = ET.SubElement(group, 'image', x=str(x * 45), y="0", width="45", height="100")
        image.set("{http://www.w3.org/1999/xlink}href", url)  # Set the xlink:href attribute

    # Create an XML tree from the SVG root element
    tree = ET.ElementTree(svg)

    # Generate the SVG as a string
    svg_string = ET.tostring(svg, encoding="utf-8").decode("utf-8")
    
    return svg_string


def update():
    while True:
        for counter in counters:
            svgs = []
            for theme in themes:
                svgs.append(create_svg(counter.count,theme))
            counter.svg = svgs
            id = counter.id
            count = counter.count
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM count WHERE id = ?', (id,))
            existing_record = cursor.fetchone()
            if existing_record:
                cursor.execute('UPDATE count SET count = ? WHERE id = ?', (count, id))
            else:
                cursor.execute('INSERT INTO count (id, count) VALUES (?, ?)', (id, count))
            conn.commit()
            conn.close()
        time.sleep(duration)

def getThemeIdByName(name):
    i = 0
    for theme in themes:
        if theme.name == name:
            return i
        i = i + 1
    return -1

def count(id):
    for counter in counters:
        if counter.id == id:
            if counter.count != MAX:
                counter.count += 1
            return counter.svg[0]
    counter = Counter(id,1)
    counters.append(counter)
    svgs = []
    for theme in themes:
        svgs.append(create_svg(1,theme))
    counter.svg = svgs
    return counter.svg[0]




class WebServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_parameters = parse_qs(parsed_url.query)
        if self.path == '/':
            self.path = '/views/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        elif re.match(r'^/get/[\w]+', self.path):
            name = self.path.split('/')[-1]
            name = name.split("?")[0]
            self.send_response(200)
            self.send_header('Content-type', 'image/svg+xml')
            self.end_headers()
            #if query_parameters["theme"] is not None:
                #theme = query_parameters["theme"]
            response = f"{str(count(name))}"
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('Not Found'.encode())



# START UP IT
print("Initializing...")
init() # Init Database

task_thread = threading.Thread(target=update) # Start Database Task
task_thread.daemon = True
task_thread.start()
print("Doe! Starting Webserver...")
# Start WebServer
with ThreadingHTTPServer((BIND, PORT), WebServer) as httpd:
    print("Done!")
    print(f"Serving at http://{BIND}:{PORT}")
    httpd.serve_forever()
