# bart-route-tracker
A simple server on [Render.com](https://render.com) and route visualizer using a [Raspberry Pi Pico W](https://www.pishop.us/product/raspberry-pi-pico-w/) with a [Pimoroni Pico Display Pack](https://shop.pimoroni.com/products/pico-display-pack?variant=32368664215635)

## What is this?
This helps for me to track the ETAs of Bay Area Rapid Transit train lines at the stop nearest my home.
[Watch a brief demonstration video here](https://github.com/n4sky/bart-route-tracker/assets/8070562/3a1a7267-9eb4-40a0-8c67-ec2514572649)

## Why not use Google Maps?
I don't like to keep glancing at my phone/computer. This is a more similar UX to a train/plane ETA board at a transit hub, which I prefer. 

## What's with the server?
The server wouldn't normally be necessary, but the BART API is behind Cloudflare, which seems to block requests that originate from Raspberry Pico Ws. The server is just middleware to make a request on behalf of the Pico W, do a bit of cleanup with the response, and then send back the data to the microcontroller.

## Links:
* [Documentation for the Pimoroni Pico Display Pack here](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/picographics/README.md#changing-the-font)

## Acknowledgements
Thanks BART for maintaining your [Legacy API](https://www.bart.gov/schedules/developers/api)
