DESCRIPTION = "Device tree overlays for Raspberry Pi cameras (stored in rootfs for deployment to /boot at boot)"
LICENSE = "Broadcom-RPi"

# Broadcom license info for RPi firmware
LIC_FILES_CHKSUM = "file://boot/LICENCE.broadcom;md5=c403841ff2837657b2ed8e5bb474ac8d"

# Use the same sources as rpi-bootfiles
RPIFW_DATE ?= "20250430"
SRCREV = "bc7f439c234e19371115e07b57c366df59cc1bc7"
SHORTREV = "${@d.getVar("SRCREV", False).__str__()[:7]}"
RPIFW_SRC_URI ?= "https://api.github.com/repos/raspberrypi/firmware/tarball/${SRCREV};downloadfilename=raspberrypi-firmware-${SHORTREV}.tar.gz"

SRC_URI = "${RPIFW_SRC_URI}"
SRC_URI[sha256sum] = "2c027debbef53c86c9ff9197d056d501b95f6ad214ad4db00a8a59b947574eb1"

S = "${WORKDIR}/raspberrypi-firmware-${SHORTREV}"

INHIBIT_DEFAULT_DEPS = "1"

DEPENDS = ""
RDEPENDS:${PN} = ""

do_configure[noexec] = "1"
do_compile[noexec] = "1"

do_install() {
    # Create directory in rootfs to store overlays temporarily
    # These will be copied to /boot/overlays/ by an init script at boot time
    install -d ${D}/usr/lib/rpi-camera-overlays
    
    # Copy all .dtbo and .dtb files from boot/overlays/
    OVERLAYS_SRC="${S}/boot/overlays"
    if [ -d "$OVERLAYS_SRC" ]; then
        for OVERLAY in "$OVERLAYS_SRC"/*.dtbo "$OVERLAYS_SRC"/*.dtb; do
            if [ -f "$OVERLAY" ]; then
                install -m 0644 "$OVERLAY" ${D}/usr/lib/rpi-camera-overlays/
            fi
        done
    fi
    
    # Create a simple script that copies overlays to /boot at first boot
    install -d ${D}${sysconfdir}/init.d
    cat > ${D}${sysconfdir}/init.d/setup-camera-overlays.sh << 'EOFSCRIPT'
#!/bin/sh
# Copy device tree overlays from /usr/lib/rpi-camera-overlays to /boot/overlays at first boot
SRC_DIR="/usr/lib/rpi-camera-overlays"
DST_DIR="/boot/overlays"
DONE_FLAG="/var/lib/rpi-camera-overlays.done"

if [ -f "$DONE_FLAG" ]; then
    exit 0
fi

# Wait for /boot to be writable
for i in 1 2 3 4 5; do
    if touch "$DST_DIR/.test.txt" 2>/dev/null && rm "$DST_DIR/.test.txt"; then
        break
    fi
    sleep 1
done

# Copy overlays if source directory exists
if [ -d "$SRC_DIR" ]; then
    mkdir -p "$DST_DIR"
    for OVERLAY in "$SRC_DIR"/*.dtbo "$SRC_DIR"/*.dtb; do
        if [ -f "$OVERLAY" ]; then
            BASENAME=$(basename "$OVERLAY")
            cp "$OVERLAY" "$DST_DIR/$BASENAME" 2>/dev/null || true
        fi
    done
    mkdir -p /var/lib
    touch "$DONE_FLAG"
fi

exit 0
EOFSCRIPT
    chmod 0755 ${D}${sysconfdir}/init.d/setup-camera-overlays.sh
}

PACKAGES = "${PN}"

FILES:${PN} = "/usr/lib/rpi-camera-overlays ${sysconfdir}/init.d/setup-camera-overlays.sh"

COMPATIBLE_MACHINE = "^rpi$"

