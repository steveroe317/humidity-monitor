This project implements a logging humidty monitor using a Raspberry Pi, a
temperature/humity sensor, a WiFi connection, and a Google FireStore database.
It is meant to automatically monitor humidity in basement, attic, or
outbuilding. 

The project can be run either as a standalone app or installed as a system
service that restarts on failure or reboot.

# UNDER CONSTRUCTION

This project is in initial development and may not work.

# Materials

Raspberry Pi with a working WiFi connection.

The WiFi connection is used to download the app's github repo
and required packages, and for logging temperature and humidty data

HiLetgo 
[DHT22/AM2302 temperature/humidty sensor](https://www.amazon.com/dp/B0795F19W6?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)

Jumper wires such as
* [Chanzon Dupont Cable Line Connector Assorted Kit Set](https://www.amazon.com/dp/B09FPGT7JT?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)
* [EdgeLec Breadboard Jumper Wires](https://www.amazon.com/dp/B07GD3KDG9?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)

# Setup

Connect the hardware components.

DHT22 AM2302 temperature/humidity sensor
* Connect the Raspberry Pi pin 20 (GND) to the DHT22 AM2302 "-" terminal
* Connect the Raspberry Pi pin 18 (GPIO24) to the DHT22 AM2302 "out" terminal
* Connect the Raspberry Pi pin 17 (3.3V) to the DHT22 AM2302 "+" terminal

Clone the humidity monitor repository and set up a virtual environment.

```
git clone https://github.com/steveroe317/humidity-monitor.git
cd humidity-monitor
python -m venv env
source env/bin/activate
python -m pip install adafruit-circuitpython-dht
```

Set up the log directory, replacing "username"
with the login that will run the trailer warmer app.

```
sudo mkdir /var/log/humidity-monitor
sudo chown username:username /var/log/humidity-monitor/
```

# Running the App

The app runs inside a python virtual environment.
It reads temperature and humidity from the sensor.
The time, temperature, and humidity are logged to a file
and written to the app's standard output.

To run the app, follow these steps:

If not already active, activate the Python virtual environment.

```
cd humidity-monitor
source env/bin/activate
```

At the root directory of the humidity-monitor repo, run

```
.humidity-monitor.py
```

The app will start emitting log messages like

```
2025/02/08 15:47:15,40,71
2025/02/08 15:48:16,40,71
2025/02/08 15:49:16,40,71
2025/02/08 15:50:16,40,71
```

These messages will also be appended to /var/log/humidity-monitor/humidity.log.
If the log file grows to over 1 megabyte in size, it will be rotated
through monitor.log.1, 2, and 3.

# Installing the App as a Linux Service

Installing the app as a system service allows it to restart after errors
or after a reboot (such as after a power outage). Follow these steps to
install it as a system service.

Modify the repo's trailer-warmer.service file for your enviroment.

* Change the WorkingDirectory entry to the trailer-warmer repo root
* Change the ExecStart entry to env/bin/python within the repo root
* Change User entry from steveroe to the login that will run the app
* Change Group entry from steveroe to the login that will run the app

Copy the modified humidity-monitor.service file to systemctl's service
directory

```
sudo cp humidity-monitor.service /etc/systemd/system
```

Make sure the app is not already running. If is, there will be resource
conflicts with the GPIO libraries.

Start the service with this command

```
sudo systemctl start humidity-monitor.service
```

Check that the service by watching for new entries in
/var/log/humidity-monitor/humidity.log

```
tail -f /var/log/humidity-monitor/humidity.log
```

and/or by running

```
sudo systemctl status humidity-monitor.service
```

systemd logs for the service can be viewd by running

```
journalctl -u humidity-monitor.service -f
```

Enable the service to start at boot by running

```
sudo systemctl enable humidity-monitor.service
```

Check that the service is enabled at boot by running

```
sudo systemctl is-enabled humidity-monitor.service
```

Service startup at boot can be tested by rebooting

```
sudo systemctl reboot
```

The service can be stopped, started, restarted, enabled, or disabled with these
commands

```
sudo systemctl stop humidity-monitor.service
sudo systemctl start humidity-monitor.service
sudo systemctl restart humidity-monitor.service
sudo systemctl enable humidity-monitor.service
sudo systemctl disable humidity-monitor.service
```

# References

[Raspberry Pi](https://www.raspberrypi.com) web page.
Hardware, software, and documentation for Raspberry Pi single
board computers and microcontrollers.


PiMyLife 
[DHT22 humidity sensor how-to](https://pimylifeup.com/raspberry-pi-humidity-sensor-dht22/)
article.
The external resistor in the article is not needed for the HiLetgo 
DHT22 AM2302 sensor.

RedHat
[systemctl how-to](https://www.redhat.com/en/blog/linux-systemctl-manage-services)
article.

Medium
[Linux service how-to](https://medium.com/@benmorel/creating-a-linux-service-with-systemd-611b5c8b91d6)
article.
