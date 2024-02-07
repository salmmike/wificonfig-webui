# Wi-Fi UI configurator
Systemd daemon for configuring Wi-Fi connections in embedded Linux devices that don't have an easily accessible UI interface.

The program creates a Wi-Fi access point after boot if a network connection isn't available.
This access point hosts a web UI that can be used for selecting a network and setting its password.

## Dependencies
The Wi-Fi UI configurator requires the host machine to have programs `iw`, `hostapd` and `uhdcpd` available.
If you wish to use different tools, feel free to add availability for them.

