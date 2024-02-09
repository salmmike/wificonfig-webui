"""
Web UI for configuring a network.

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
from flask import Flask, render_template, request, redirect, url_for

import wifi

app = Flask("wificonfigurator-webui")

CERT_KEY = "/etc/wificonfigurator.d/key.pem"
CERT_CRT = "/etc/wificonfigurator.d/cert.pem"

usernames = [x.ssid for x in wifi.Cell.all("wlp0s20f3")]


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
        print(username, password)
    return render_template("login.html", usernames=usernames)


def run(cert: str, key: str, http: bool):
    """Run the WebUI"""
    if http:
        app.run()
    else:
        app.run(host="0.0.0.0", port=5000, ssl_context=(cert, key))


def main():
    """Parse command line arguments and run"""
    argparser = argparse.ArgumentParser(
        prog="wificonfigurator-webui",
        description="Host a webUI on localhost for configuring Wi-Fi",
    )
    argparser.add_argument("-c", "--certificate", default=CERT_CRT)
    argparser.add_argument("-k", "--key", default=CERT_KEY)
    argparser.add_argument("--http", default=False)
    args = vars(argparser.parse_args())

    run(args.get("certificate"), args.get("key"), args.get("http"))

if __name__ == "__main__":
    main()
