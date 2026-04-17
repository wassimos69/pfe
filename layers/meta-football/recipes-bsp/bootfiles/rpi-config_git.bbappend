# Raspberry Pi 5 Official Active Cooler tuning in boot config.txt.
# Temperatures are in millicelsius and speed is PWM 0-255.
# Boot optimizations: disable camera detection (manual load), reduce gpu_mem, enable turbo
RPI_EXTRA_CONFIG = "\
[pi5]\n\
camera_auto_detect=0\n\
dtoverlay=imx477,cam0\n\
gpu_mem=32\n\
force_turbo=0\n\
initrd_high=0xffffffff\n\
disable_audio=1\n\
dtparam=cooling_fan=on\n\
dtparam=fan_temp0=60000\n\
dtparam=fan_temp0_hyst=5000\n\
dtparam=fan_temp0_speed=0\n\
dtparam=fan_temp1=67000\n\
dtparam=fan_temp1_hyst=5000\n\
dtparam=fan_temp1_speed=110\n\
dtparam=fan_temp2=74000\n\
dtparam=fan_temp2_hyst=5000\n\
dtparam=fan_temp2_speed=180\n\
dtparam=fan_temp3=80000\n\
dtparam=fan_temp3_hyst=5000\n\
dtparam=fan_temp3_speed=255\n\
[all]\n\
"
