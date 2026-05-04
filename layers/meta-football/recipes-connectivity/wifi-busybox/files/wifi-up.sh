#!/bin/sh
set -eu

IFACE="${IFACE:-}"
WPA_CONF="/etc/wpa_supplicant/wpa_supplicant.conf"

if [ -z "$IFACE" ]; then
	if [ -d /sys/class/net/wlan0 ]; then
		IFACE="wlan0"
	else
		for netdev in /sys/class/net/*; do
			[ -e "$netdev/wireless" ] || continue
			IFACE="${netdev##*/}"
			break
		done
	fi
fi

if [ -z "$IFACE" ]; then
	echo "wifi-up: no wireless interface detected, skipping" >&2
	exit 0
fi

if [ ! -f "$WPA_CONF" ]; then
	echo "wifi-up: missing $WPA_CONF" >&2
	exit 1
fi

ip link set "$IFACE" up

# Restart wpa_supplicant for this interface to avoid stale config/process issues.
pkill -f "wpa_supplicant.*-i[[:space:]]*$IFACE" >/dev/null 2>&1 || true
wpa_supplicant -B -i "$IFACE" -c "$WPA_CONF"

# Give WPA association enough time before requesting DHCP.
i=0
connected=0
while [ "$i" -lt 30 ]; do
	if iw dev "$IFACE" link 2>/dev/null | grep -q "Connected to"; then
		connected=1
		break
	fi
	i=$((i + 1))
	sleep 1
done

if [ "$connected" -ne 1 ]; then
	echo "wifi-up: interface $IFACE did not associate within timeout" >&2
	exit 1
fi

exec udhcpc -i "$IFACE" -q -t 10 -T 3
