NOTE: this project is based heavily on https://github.com/Olen/VictronConnect
NOTE2: this is at the momet under heavy development, in other words the code is broken ;-)

This is a completely private project. It is my personal approach to try to connect to my Victron device: BlueSolar MPPT 75/15 with Bluetooth Smart Dongle.
My program is currently running on a Raspberry 3 with Raspbian.

The approach is to run this program once every minute via a cron job. The data will be stored to an InfluxDB.
