SRC_URI = "git://github.com/raspberrypi/libcamera.git;protocol=https;branch=main"
SRCREV = "fe601eb6ffe02922ff980c60621dd79d401d9061"
PV = "0.7.0+git${SRCPV}"

DEPENDS:append = " libpisp"

# Force PiSP on RPi5 using libcamera's canonical variables.
LIBCAMERA_PIPELINES:rpi = "rpi/pisp"
LIBCAMERA_IPAS:rpi = "rpi/pisp"

# Drop vc4-oriented PACKAGECONFIG injected by lower-priority layers.
PACKAGECONFIG:remove = "raspberrypi"

do_install:append() {
	install -d ${D}${libdir}/libcamera/ipa/rpi
	if [ -f ${D}${libdir}/libcamera/ipa/ipa_rpi_pisp.so ]; then
		install -m 0755 ${D}${libdir}/libcamera/ipa/ipa_rpi_pisp.so ${D}${libdir}/libcamera/ipa/rpi/
	fi
	if [ -f ${D}${libdir}/libcamera/ipa/ipa_rpi_pisp.so.sign ]; then
		install -m 0644 ${D}${libdir}/libcamera/ipa/ipa_rpi_pisp.so.sign ${D}${libdir}/libcamera/ipa/rpi/
	fi
}

FILES:${PN}:append = " ${libdir}/libcamera/ipa/rpi/*"
