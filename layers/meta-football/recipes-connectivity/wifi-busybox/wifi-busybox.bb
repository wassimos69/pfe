SUMMARY = "Wi-Fi autostart using BusyBox udhcpc and wpa_supplicant"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://wifi-up.sh \
    file://wpa_supplicant.conf \
    file://wifi-up.service \
"

S = "${WORKDIR}"

inherit systemd

RDEPENDS:${PN} = "busybox wpa-supplicant iw"
SYSTEMD_SERVICE:${PN} = "wifi-up.service"
SYSTEMD_AUTO_ENABLE:${PN} = "enable"

do_install() {
    install -d ${D}/usr/local/bin
    install -m 0755 ${WORKDIR}/wifi-up.sh ${D}/usr/local/bin/wifi-up.sh

    install -d ${D}${sysconfdir}/wpa_supplicant
    install -m 0600 ${WORKDIR}/wpa_supplicant.conf ${D}${sysconfdir}/wpa_supplicant/wpa_supplicant.conf

    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/wifi-up.service ${D}${systemd_system_unitdir}/wifi-up.service
}

FILES:${PN} += " \
    /usr/local/bin/wifi-up.sh \
    ${sysconfdir}/wpa_supplicant/wpa_supplicant.conf \
    ${systemd_system_unitdir}/wifi-up.service \
"
