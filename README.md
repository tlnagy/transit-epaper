# transit-epaper
Download bus info from Transit.app and update a Waveshare ePaper screen on a Raspberry Pi

Git clone this directory into your home, make a new file called .appsecrets in your home directory and replace XXXXX with your API key from Transit.app

```
#!/bin/bash
#filename: .appsecrets
export TRANSIT_APIKEY=XXXXXXXXXXXX
```
Now you have cp the `*.service` and `*.timer` to `/etc/systemd/system` and then run `sudo systemctl daemon-reload` to load them, followed by `sudo systemctl enable` for each timer. Naturally, you should edit the timers to match your desired behavior.

