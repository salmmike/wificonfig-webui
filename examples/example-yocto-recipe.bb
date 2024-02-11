
DESCRIPTION = "Wifi configuration WebUI application"
LICENSE = "CLOSED"

SRC_URI = "git://github.com/salmmike/wificonfig-webui.git;branch=master;protocol=https;"
SRC_URI:append = " file://wpa_supplicant.template "
SRC_URI:append = " file://51-wireless.network "

SRCREV = "${AUTOREV}"

S = "${WORKDIR}/git"


RDEPENDS:${PN} += " python3 \
		    python3-flask \
		    python3-requests \
		    hostapd \
		    bash "

SYSTEMD_AUTO_ENABLE = "enable"
SYSTEMD_SERVICE:${PN} = "wificonfigurator-webui.service"
SYSTEMD_SERVICE:${PN} += "wificonfigurator-accesspoint.service"

FILES:${PN} += "${systemd_unitdir}/system/wificonfigurator-webui.service \
		${systemd_unitdir}/network/51-wireless.network"

do_install:append() {
  install -d ${D}/${systemd_unitdir}/system
  install -d ${D}/${systemd_unitdir}/network
  install -d ${D}/${bindir}
  install -d ${D}/${sysconfdir}
  install -d ${D}/${sysconfdir}/wificonfigurator.d

  install -m 0644 ${S}/systemd/wificonfigurator-webui.service ${D}/${systemd_unitdir}/system
  install -m 0644 ${S}/systemd/wificonfigurator-accesspoint.service ${D}/${systemd_unitdir}/system
  install -m 0777 ${S}/setup-scripts/wificonfig-certificates ${D}/${bindir}
  install -m 0777 ${S}/setup-scripts/create-ap-interface ${D}/${bindir}
  install -m 0777 ${S}/setup-scripts/wificonfig-check-connection ${D}/${bindir}
  install -m 0644 ${S}/examples/wificonfigurator.conf ${D}/${sysconfdir}
  install -m 0644 ${WORKDIR}/wpa_supplicant.template ${D}/${sysconfdir}/wificonfigurator.d
  install -m 0644 ${WORKDIR}/51-wireless.network ${D}/${systemd_unitdir}/network
}

inherit setuptools3 systemd
