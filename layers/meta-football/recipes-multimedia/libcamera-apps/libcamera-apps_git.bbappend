SRC_URI = "git://github.com/raspberrypi/libcamera-apps.git;protocol=https;branch=main"
SRCREV = "8b7be4ebfe185fa938a340a0125f023bd1d8227e"
PV = "1.11.1+git${SRCPV}"

PACKAGECONFIG[libav] = "-Denable_libav=enabled,-Denable_libav=disabled,libav"
PACKAGECONFIG[drm] = "-Denable_drm=enabled,-Denable_drm=disabled,libdrm"
PACKAGECONFIG[egl] = "-Denable_egl=enabled,-Denable_egl=disabled,virtual/egl"
PACKAGECONFIG[qt] = "-Denable_qt=enabled,-Denable_qt=disabled,qtbase"
PACKAGECONFIG[opencv] = "-Denable_opencv=enabled,-Denable_opencv=disabled,opencv"
PACKAGECONFIG[tflite] = "-Denable_tflite=enabled,-Denable_tflite=disabled,tensorflow-lite"

FILES:${PN}:append = " \
	${datadir}/rpi-camera-assets \
	${libdir}/rpicam-apps-postproc \
	${libdir}/rpicam-apps-preview \
"
