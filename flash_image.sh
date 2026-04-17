#!/bin/bash
# Automated SD card flashing script for RPi5 minimal image

set -e  # Exit on error

IMAGE_PATH="/home/wassim/Bureau/yocto/clean/build/tmp/deploy/images/raspberrypi5"
IMAGE_FILE="${IMAGE_PATH}/rpi5-minimal-raspberrypi5.rootfs.wic.gz"
LATEST_IMAGE=$(ls -t "${IMAGE_PATH}"/rpi5-minimal*.wic.gz | head -1)

echo "=========================================="
echo "RPi5 Minimal Image Flash Script"
echo "=========================================="
echo ""

# Check if image exists
if [ ! -f "$LATEST_IMAGE" ]; then
    echo "ERROR: Image not found at $LATEST_IMAGE"
    exit 1
fi

echo "Image file: $(basename $LATEST_IMAGE)"
echo "Image size: $(du -h $LATEST_IMAGE | cut -f1)"
echo ""

# List available USB devices
echo "Available USB devices (potential SD card locations):"
lsblk -d -o NAME,SIZE,TYPE | grep -v loop || true
echo ""

# Prompt for device selection
read -p "Enter the target device (e.g., /dev/sda, /dev/sdb): " DEVICE

if [ -z "$DEVICE" ]; then
    echo "ERROR: No device specified"
    exit 1
fi

# Validate device exists
if [ ! -e "$DEVICE" ]; then
    echo "ERROR: Device $DEVICE not found"
    exit 1
fi

# Double-check with user
echo ""
echo "⚠️  WARNING: This will erase ALL data on $DEVICE"
DEVICE_NAME=$(lsblk -d -o NAME,SIZE "$DEVICE" | tail -1)
echo "Device: $DEVICE_NAME"
read -p "Are you absolutely sure? Type 'yes' to confirm: " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Flashing image..."
echo "This may take 2-3 minutes..."
echo ""

# Flash the image
zcat "$LATEST_IMAGE" | sudo dd of="$DEVICE" bs=4M conv=fsync status=progress

echo ""
echo "✅ Flash complete!"
echo ""
echo "Next steps:"
echo "1. Eject the SD card: sudo eject $DEVICE"
echo "2. Insert SD card into RPi5"
echo "3. Connect UART serial cable to debug UART (GPIO14/15)"
echo "4. Power on the Pi"
echo "5. Monitor boot: picocom -b 115200 /dev/ttyUSB0"
echo "6. At first boot, setup-camera-overlays.sh will copy overlays to /boot/overlays/"
echo "7. Run: libcamera-hello --list-cameras"
echo "8. Expected output: 'Available cameras / 0 : imx477 [4608x3456]'"
echo ""
