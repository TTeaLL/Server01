import json
import urllib.parse
from http import server


class CustomHandler(server.SimpleHTTPRequestHandler):
    lines = []
    file = None

    try:
        file = open('RU.txt', 'r', encoding="utf-8")
        lines = file.readlines()
    finally:
        file.close()

    lines = [line.split('\t') for line in lines]

    def do_GET(self):
        content = {"error": True}
        p = self.path.split('?')

        if p[0] == '/geonameid':
            geonameid = p[1].split('=')
            id = geonameid[1]

            city = [line for line in self.lines if id == line[0] and "P" == line[6]]
            content = {
                "error": False,
                "city": city

            }

        elif p[0] == '/geolist':
            page_param = p[1].split('&')
            page_number = page_param[0].split('=')
            page_lenght = page_param[1].split('=')

            page_number = int(page_number[1])
            page_lenght = int(page_lenght[1])

            cities = [line for line in self.lines if line[6] == "P"]

            cities = cities[(page_number - 1) * page_lenght:page_number * page_lenght]
            content = {"error": False,
                       "cities": cities}

        elif p[0] == '/tip':
            tip_message = p[1].split('=')
            city_part_name = tip_message[1]
            city_part_name1 = urllib.parse.unquote(city_part_name)

            tip = [name for line in self.lines for name in line[3].split(',') if
                   city_part_name1.lower() in name.lower()]
            content = {
                "error": False,
                "tip": tip
            }

        elif p[0] == '/geocompare':

            compared_cities = p[1].split('&')
            first_city = compared_cities[0].split('=')
            second_city = compared_cities[1].split('=')
            first_city = urllib.parse.unquote(first_city[1])
            second_city = urllib.parse.unquote(second_city[1])

            first_city = sorted([line for line in self.lines if first_city in line[3].split(',')], key=lambda x: x[14])
            second_city = sorted([line for line in self.lines if second_city in line[3].split(',')], key=lambda x: x[14])

            first_city = first_city[-1] if first_city else None
            second_city = second_city[-1] if second_city else None

            north_city = first_city if first_city[4] > second_city[4] else second_city

            time_zone_equal = first_city[17] == second_city[17]

            content = {"error": False,
                       "first_city": first_city,
                       "second_city": second_city,
                       "north_city": north_city,
                       "time_zone_equal": time_zone_equal}

        else:
            content["error_msg"] = "Bad request"

        content = json.dumps(content)
        content = content.encode('utf-8')

        self.protocol_version = 'HTTP/1.1'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')

        self.end_headers()
        self.wfile.write(content)


server_address = ('127.0.0.1', 8000)
http = server.HTTPServer(server_address, CustomHandler)
http.serve_forever()
