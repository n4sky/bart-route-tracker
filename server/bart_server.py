from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
import requests
import secrets

# Replace 'your_station_abbr' with the BART station abbreviation of your choice.
# https://api.bart.gov/docs/overview/abbrev.aspx
station_abbr = "your_station_abbr"

''' Function takes in a station abbreviation 
    and an API key to the BART API and returns one
    of two objects:
    1)  a dict with "Error" as a single key, explaining the issue
    2)  a dict containing destination keys, each mapped 
        to ETAs in minutes as strings,
        e.g. "Berryessa" : ["2", "5", "27"]
'''
def get_bart_arrival_times(station_abbr, api_key):
    base_url = "https://api.bart.gov/api/etd.aspx"
    
    params = {
        "cmd": "etd",
        "orig": station_abbr,
        "key": api_key,
        "dir": "s", #southbound
        "json": "y"
    }

    results = {}

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if "root" not in data: raise Exception("No 'root' object found in API response")
        data = data["root"]

        if "station" not in data: raise Exception("No station data found")
        data = data["station"][0] # 0 gets us the one and only object in the station list

        if "etd" not in data: raise Exception("No departure times found")
        data = data["etd"] # etd gets us the list of all the trains (and all times) for that station

        # iterate over the many destinations
        for line in data:
            destination = line["destination"]

            etas = []
            estimates = line['estimate']
            for estimate in estimates:
                mins = estimate['minutes']
                etas.append(mins)
            results[destination] = etas
            
    except Exception as e:
        results = {}
        results["Error"] = str(e)

    return results


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        results = get_bart_arrival_times(station_abbr, secrets.API_KEY)
        response = json.dumps(results)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(response, "utf-8"))

        print(self.path)

if __name__ == "__main__":        

    # server config - specified by Render.io, our hosting service
    # see "Host and Port Configuration" here: https://render.com/docs/web-services
    host_name = "0.0.0.0"
    server_port = 10000

    webServer = HTTPServer((host_name, server_port), MyServer)
    print("Server started http://%s:%s" % (host_name, server_port))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

    







