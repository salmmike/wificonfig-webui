"""
Web UI for configuring a WiFi network.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
USA

Author: Mike Salmela
"""

import argparse
import subprocess
import pathlib
import threading
import time
import random
import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify


CERT_KEY = "/etc/wificonfigurator.d/key.pem"
CERT_CRT = "/etc/wificonfigurator.d/cert.pem"


class WificonfigWebUI:
    """
    Hosts a WebUI for configuring Wi-Fi connection and creates configuration files.
    """

    def __init__(self, args: dict) -> None:
        self._app = None
        self._args = args
        self._connection_tried = False
        self._connected = False
        self._simulate = args.get("simulate")

    @property
    def ssids(self):
        """List of found SSIDs"""
        if self._simulate:
            return ["Test1", "Test2", "Test3"]

        return list(
            filter(
                None,
                [
                    x.strip().split(": ")[1] if x.count("SSID") else None
                    for x in subprocess.check_output(
                        ["iw", "dev", "wlan0", "scan"], encoding="UTF-8"
                    ).split("\n")
                ],
            )
        )

    @property
    def wpa_supplicant_file(self) -> str:
        """Path to WPA supplicant config file"""
        interface = self._args.get("wifi_interface")
        return f"/etc/wpa_supplicant/wpa_supplicant-{interface}.conf"

    def _create_wpa_supplicant_config(self, username: str, password: str):
        if self._simulate:
            return

        template_file: str = self._args.get("wpa_template")
        template = ""

        with open(template_file, encoding="utf-8") as template_f:
            template = template_f.read()

        wpa_config_end = subprocess.check_output(
            ["wpa_passphrase", username, password], encoding="utf-8"
        ).replace(f'#psk="{password}"', "")
        template += "\n" + wpa_config_end

        pathlib.Path("/etc/wpa_supplicant/").mkdir(exist_ok=True)

        with open(self.wpa_supplicant_file, "w", encoding="utf-8") as configfile:
            configfile.write(template)

    def _connect_network(self):
        logging.debug("Connecting to %s", self._args.get("wifi_interface"))
        if self._simulate:
            time.sleep(5)
            self._connection_tried = True
            self._connected = random.random() > 0.5
            print("Connected:", self._connected)
            return
        res = subprocess.call(
            ["wificonfig-check-connection", self._args.get("wifi_interface")]
        )
        self._connection_tried = True
        if res == 0:
            self._connected = True
            self._stop_service()

    def _stop_service(self):
        time.sleep(3)  # Allow time for UI.
        subprocess.run(
            ["systemctl", "stop", "wificonfigurator-accesspoint"], check=True
        )
        subprocess.run(["systemctl", "stop", "wificonfigurator-webui"], check=True)

    def connect_network(self, username: str, password: str):
        """Try connecting to a network."""
        self._connection_tried = False
        self._connected = False
        self._create_wpa_supplicant_config(username, password)
        configthread = threading.Thread(target=self._connect_network)
        configthread.start()

    def make_app(self):
        """Create the Flask app"""
        app = Flask(__name__)

        @app.route("/")
        def index():
            """Redirect to login page"""
            return redirect(url_for("login"))

        @app.route("/login", methods=["GET", "POST"])
        def login():
            """Login page"""
            if request.method == "POST":
                username = request.form["username"]
                password = request.form["password"]
                self.connect_network(username, password)
                return render_template("connecting.html")
            return render_template("login.html", usernames=self.ssids)

        @app.route("/network_status")
        def network_status():
            """Get the network status in JSON format."""
            return jsonify(
                {
                    "connecting_tried": self._connection_tried,
                    "connected": self._connected,
                }
            )

        self._app = app

    def run(self, cert: str, key: str, http: bool):
        """Run the Flask application"""
        if not self._app:
            raise RuntimeError("Application not initialized!")
        if http:
            self._app.run()
        else:
            self._app.run(host="0.0.0.0", port=5001, ssl_context=(cert, key))


def run(cert: str, key: str, http: bool, args: dict):
    """Run the WebUI"""
    app = WificonfigWebUI(args)
    app.make_app()
    app.run(cert, key, http)


def main():
    """Parse command line arguments and run"""
    argparser = argparse.ArgumentParser(
        prog="wificonfigurator-webui",
        description="Host a webUI on localhost for configuring Wi-Fi",
    )
    argparser.add_argument("-c", "--certificate", default=CERT_CRT)
    argparser.add_argument("-k", "--key", default=CERT_KEY)
    argparser.add_argument("--http", default=False)
    argparser.add_argument("--wpa-template")
    argparser.add_argument("--wifi-interface")
    argparser.add_argument("--simulate", action="store_true", default=False)

    args = vars(argparser.parse_args())

    run(args.get("certificate"), args.get("key"), args.get("http"), args)


if __name__ == "__main__":
    main()
