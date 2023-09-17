# BART Route Tracker
This lets me track the ETAs of Bay Area Rapid Transit train lines at the stop nearest my home. I can more efficiently plan walks to the station using this information.
[Watch a brief demonstration video here](https://github.com/n4sky/bart-route-tracker/assets/8070562/3a1a7267-9eb4-40a0-8c67-ec2514572649)

<img width="875" alt="image" src="https://github.com/n4sky/bart-route-tracker/assets/8070562/561f7a97-e2fd-412e-a444-e24d889f3531">

## What are the different components?
1) A simple server hosted on [Render.com](https://render.com) (written in Python), and
2) A route visualizer using a [Raspberry Pi Pico W](https://www.pishop.us/product/raspberry-pi-pico-w/) with a [Pimoroni Pico Display Pack](https://shop.pimoroni.com/products/pico-display-pack?variant=32368664215635) (written in Micropython, specifically Pimoroni's [distribution](https://github.com/pimoroni/pimoroni-pico)

## Why not just use Google Maps?
I don't like to keep glancing at my phone and computer. This is a similar experience to a train/plane/bus ETA board at a transit hub, which I prefer. 

## What's with the server?
The server wouldn't normally be necessary, but the BART API is behind Cloudflare; Cloudflare seems to block requests that originate from the Raspberry Pico W. The server is just middleware to make a request on behalf of the Pico W, perform a bit of cleanup with the response, and then send back the relevant response data to the microcontroller.

## Links:
* [Documentation for the Pimoroni Pico Display Pack here](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/picographics/README.md#changing-the-font)

## Acknowledgements
Thanks BART for maintaining your [Legacy API](https://www.bart.gov/schedules/developers/api)
