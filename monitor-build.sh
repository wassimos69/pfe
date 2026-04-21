#!/bin/bash

cd /home/wassim/Bureau/yocto/clean/build

echo "🚀 BitBake systemd Build Monitor"
echo "=================================="
echo ""

while true; do
  clear
  
  echo "📊 BUILD STATUS"
  echo "Time: $(date '+%H:%M:%S %Y-%m-%d')"
  echo ""
  
  # Check build size
  TMP_SIZE=$(du -sh tmp 2>/dev/null | awk '{print $1}')
  SSTATE_SIZE=$(du -sh sstate-cache 2>/dev/null | awk '{print $1}')
  echo "📁 Storage:"
  echo "   tmp/: $TMP_SIZE"
  echo "   sstate-cache/: $SSTATE_SIZE"
  echo ""
  
  # Check processes
  BITBAKE_PROCESSES=$(ps aux | grep "bitbake-server" | grep -v grep | wc -l)
  GCC_TASKS=$(ps aux | grep -E "gcc|cc1|collect2" | grep -v grep | wc -l)
  echo "⚙️  Active tasks:"
  echo "   BitBake servers: $BITBAKE_PROCESSES"
  echo "   Compilation: $GCC_TASKS"
  echo ""
  
  # Check log
  if [ -f bitbake-cookerdaemon.log ]; then
    echo "📝 Recent log:"
    tail -2 bitbake-cookerdaemon.log | tail -1 | sed 's/^[^ ]* [^ ]* /   /'
  fi
  
  # Check if build finished
  if ! ps aux | grep -q "bitbake rpi5-minimal" | grep -v grep; then
    echo ""
    echo "✅ BUILD COMPLETED!"
    break
  fi
  
  echo ""
  echo "Press Ctrl+C to stop monitoring (refresh every 5s)"
  sleep 5
done
