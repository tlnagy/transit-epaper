# transit-epaper

![](https://github.com/tlnagy/transit-epaper/blob/7e2acfa8cc73d3a32db842099b64e3836a88e5ce/bus.png)

Download bus info from Transit.app and update a Waveshare ePaper screen on a Raspberry Pi

Git clone this directory into your home using `git clone --recurse-submodules`, make a new file called .appsecrets in your home directory and replace XXXXX with your API key from Transit.app

```
#!/bin/bash
#filename: .appsecrets
export TRANSIT_APIKEY=XXXXXXXXXXXX
```
Then you can copy the `*.service` and `*.timer` to `/etc/systemd/system` and then run `sudo systemctl daemon-reload` to load them, followed by `sudo systemctl enable` for each timer. Naturally, you should edit the timers to match your desired behavior.

