SUMMARY = "Image ultra minimale RPi5 (boot + shell)"
LICENSE = "MIT"

require recipes-core/images/core-image-minimal.bb

IMAGE_FEATURES:remove = "package-management splash debug-tweaks"
IMAGE_FEATURES:append = " ssh-server-openssh"

# Use dynamic rootfs sizing from actual package contents.

ENABLE_UART = "1"

inherit extrausers



# Set root password to: root (for lab/testing only)
# Also create the 'netdev' group for wpa_supplicant control interface
EXTRA_USERS_PARAMS = "usermod -p '\$6\$fRq/7X3UHnR/ag/I\$IMk1SsCcUoIqnr0pjCCEhxOUzkoyEaCTqg/.OG4L3aXPRw5bKYDGwJJyX7fDiEKAHYN9Bry9EoZHyXpL.fz.y1' root; groupadd -f netdev;"

# We need to add the necessary packages for Wi-Fi, Ethernet and SSH support
CORE_IMAGE_EXTRA_INSTALL += " \
    wpa-supplicant \
    wpa-supplicant-cli \
    wpa-supplicant-passphrase \
    parted \
    e2fsprogs-resize2fs \
    iw \
    wireless-regdb-static \
    linux-firmware-rpidistro-bcm43455 \
    kernel-module-brcmfmac \
    kernel-module-brcmfmac-wcc \
    kernel-module-brcmutil \
    kernel-module-cfg80211 \
    kernel-module-rfkill \
    kernel-module-rp1 \
    kernel-module-bcm2835-unicam \
    kernel-module-rp1-cfe \
    kernel-module-i2c-designware-core \
    kernel-module-i2c-designware-platform \
    kernel-module-i2c-dev \
    kernel-module-imx477 \
    kernel-module-v4l2-async \
    kernel-module-v4l2-cci \
    kernel-module-v4l2-fwnode \
    kernel-module-v4l2-mem2mem \
    kernel-module-videobuf2-common \
    kernel-module-videobuf2-dma-contig \
    kernel-module-videobuf2-memops \
    kernel-module-videobuf2-v4l2 \
    kernel-module-pisp-be \
    kernel-module-pwm-fan \
    kernel-module-gpio-fan \
    libcamera \
    libcamera-apps \
    libpisp \
"

# Allow SSH root login with password for bring-up/testing.
set_ssh_login_policy() {
    install -d ${IMAGE_ROOTFS}${sysconfdir}/ssh/sshd_config.d
    cat > ${IMAGE_ROOTFS}${sysconfdir}/ssh/sshd_config.d/10-root-password.conf << 'EOF'
PermitRootLogin yes
PasswordAuthentication yes
KbdInteractiveAuthentication no
EOF
}

# Setup wpa_supplicant control socket directory with proper permissions
setup_wpa_supplicant_dir() {
    install -d -m 0770 ${IMAGE_ROOTFS}/var/run/wpa_supplicant
    # The netdev group will be created, so this directory can be properly owned
}

setup_wifi_autoconnect() {
    install -d ${IMAGE_ROOTFS}${sysconfdir}/wpa_supplicant
    install -d ${IMAGE_ROOTFS}${sysconfdir}/network
    install -d ${IMAGE_ROOTFS}${sysconfdir}/init.d
    install -d ${IMAGE_ROOTFS}${sysconfdir}/rc3.d

    # Install user-provided Wi-Fi credentials for automatic boot connection.
    install -m 0600 ${THISDIR}/files/wpa_supplicant.conf \
        ${IMAGE_ROOTFS}${sysconfdir}/wpa_supplicant/wpa_supplicant-wlan0.conf

    # Install network interfaces config
    install -m 0644 ${THISDIR}/files/network-interfaces \
        ${IMAGE_ROOTFS}${sysconfdir}/network/interfaces

    # Install wpa_supplicant init.d script
    install -m 0755 ${THISDIR}/files/wpa_supplicant.init \
        ${IMAGE_ROOTFS}${sysconfdir}/init.d/wpa_supplicant

    # Create rc.d symlink for wpa_supplicant
    ln -sf ../init.d/wpa_supplicant ${IMAGE_ROOTFS}${sysconfdir}/rc3.d/S81wpa_supplicant || true
}

setup_camera_modules_load() {
    install -d ${IMAGE_ROOTFS}${sysconfdir}/modules-load.d
    cat > ${IMAGE_ROOTFS}${sysconfdir}/modules-load.d/rpi5-platform.conf << 'EOF'
i2c-designware-core
i2c-designware-platform
i2c-dev
v4l2-cci
brcmfmac
brcmutil
cfg80211
rfkill
pwm_fan
gpio_fan
EOF
}

setup_camera_module_service() {
    install -d ${IMAGE_ROOTFS}${sbindir}
    install -d ${IMAGE_ROOTFS}${sysconfdir}/init.d
    install -d ${IMAGE_ROOTFS}${sysconfdir}/rcS.d
    
    cat > ${IMAGE_ROOTFS}${sbindir}/camera-module-init.sh <<"CAMEOF"
#!/bin/sh
set -eu

modprobe i2c-designware-core || true
modprobe i2c-designware-platform || true
modprobe i2c-dev || true
modprobe v4l2-cci || true

# Retry sensor bind with minimal delays (early boot can fail with I2C error -5).
ok=0
bound_path=""
for try in 1 2 3; do
    echo "camera-module-init: probe attempt ${try}"
    modprobe -r pisp-be 2>/dev/null || true
    modprobe -r rp1-cfe 2>/dev/null || true
    modprobe -r imx477 2>/dev/null || true

    modprobe imx477 || true
    for p in /sys/bus/i2c/drivers/imx477/*-001a; do
        if [ -e "${p}" ]; then
            bound_path="${p}"
            ok=1
            break
        fi
    done
    if [ "${ok}" -eq 1 ]; then
        ok=1
        echo "camera-module-init: imx477 bound on ${bound_path##*/}"
        break
    fi
    [ ${try} -lt 3 ] && sleep 0.5
done

if [ "${ok}" -ne 1 ]; then
    echo "camera-module-init: imx477 did not bind after retries"
fi

# Keep the pipeline loaded even if the first probe window was late.
modprobe rp1-cfe || true
modprobe pisp-be || true

lsmod | grep -E 'imx477|rp1_cfe|pisp_be|videobuf2|v4l2' || true
CAMEOF
    chmod 0755 ${IMAGE_ROOTFS}${sbindir}/camera-module-init.sh

    # Install init.d script from file
    install -m 0755 ${THISDIR}/files/camera-module-init.init \
        ${IMAGE_ROOTFS}${sysconfdir}/init.d/camera-module-init

    # Create rc.S symlink for early boot (before multi-user)
    ln -sf ../init.d/camera-module-init ${IMAGE_ROOTFS}${sysconfdir}/rcS.d/S02camera-module-init || true
}

setup_rootfs_autogrow() {
    install -d ${IMAGE_ROOTFS}${sbindir}
    install -d ${IMAGE_ROOTFS}${sysconfdir}/init.d
    install -d ${IMAGE_ROOTFS}${sysconfdir}/rcS.d
    
    cat > ${IMAGE_ROOTFS}${sbindir}/rpi-rootfs-autogrow.sh <<"ROOTEOF"
#!/bin/sh
set -eu

MARKER=/etc/.rootfs-resized
[ -f "${MARKER}" ] && exit 0

rootdev="$(findmnt -n -o SOURCE / || true)"
[ -n "${rootdev}" ] || exit 0

if [ -L "${rootdev}" ]; then
    rootdev="$(readlink -f "${rootdev}")"
fi

disk=""
partnum=""
case "${rootdev}" in
    /dev/mmcblk*p[0-9]*|/dev/nvme*n*p[0-9]*)
        disk="${rootdev%p*}"
        partnum="${rootdev##*p}"
        ;;
    /dev/sd[a-z][0-9]*)
        disk="${rootdev%[0-9]*}"
        partnum="${rootdev##*[!0-9]}"
        ;;
    *)
        exit 0
        ;;
esac

[ -n "${disk}" ] && [ -n "${partnum}" ] || exit 0

parted -s "${disk}" "resizepart ${partnum} 100%"
partprobe "${disk}" || true
sleep 2
resize2fs "${rootdev}" || true

touch "${MARKER}"
ROOTEOF
    chmod 0755 ${IMAGE_ROOTFS}${sbindir}/rpi-rootfs-autogrow.sh

    # Install init.d script from file
    install -m 0755 ${THISDIR}/files/rpi-rootfs-autogrow.init \
        ${IMAGE_ROOTFS}${sysconfdir}/init.d/rpi-rootfs-autogrow

    # Create rc.S symlink for very early boot
    ln -sf ../init.d/rpi-rootfs-autogrow ${IMAGE_ROOTFS}${sysconfdir}/rcS.d/S01rpi-rootfs-autogrow || true
}
#
ROOTFS_POSTPROCESS_COMMAND += "set_ssh_login_policy; setup_wpa_supplicant_dir; setup_wifi_autoconnect; setup_camera_modules_load; setup_camera_module_service; setup_rootfs_autogrow; "

# Chargement automatique des modules au boot
# Les noms de modules utilisent des underscores (pas des tirets)
KERNEL_MODULE_AUTOLOAD += "imx477 bcm2835_unicam rp1_cfe pisp_be v4l2_async v4l2_fwnode v4l2_cci v4l2_mem2mem videobuf2_common videobuf2_dma_contig videobuf2_memops videobuf2_v4l2 brcmfmac brcmutil cfg80211 rfkill pwm_fan gpio_fan"


# Suppression de dossier de travail après la création de l'image pour économiser de l'espace disque
INHERIT += "rm_work"

# === Camera Configuration ===
# libcamera_git.bb from meta-football provides RPi-optimized libcamera
# Automatically selected over meta-oe's 0.4.0 version (git > versioned-release)

DISTRO_FEATURES:append = " libcamera"

