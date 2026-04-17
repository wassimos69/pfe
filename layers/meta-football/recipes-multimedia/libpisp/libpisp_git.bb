SUMMARY = "Raspberry Pi PiSP helper library"
HOMEPAGE = "https://github.com/raspberrypi/libpisp"
LICENSE = "BSD-2-Clause"
LIC_FILES_CHKSUM = "file://LICENSES/BSD-2-Clause.txt;md5=3417a46e992fdf62e5759fba9baef7a7"

SRC_URI = "git://github.com/raspberrypi/libpisp.git;protocol=https;branch=main"
SRCREV = "15e11061b9e856f94d6fcd8b09dea79b88b4d953"
PV = "1.3.0+git${SRCPV}"

S = "${WORKDIR}/git"

DEPENDS = "nlohmann-json"

inherit meson pkgconfig

EXTRA_OEMESON = " \
    -Dlogging=disabled \
    -Dgstreamer=disabled \
    -Dexamples=false \
"
