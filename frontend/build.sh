#!/bin/bash
set -e

FLUTTER_VERSION="3.22.2"
FLUTTER_URL="https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_${FLUTTER_VERSION}-stable.tar.xz"

echo "Installing Flutter $FLUTTER_VERSION..."
curl -fsSL "$FLUTTER_URL" -o /tmp/flutter.tar.xz
tar xf /tmp/flutter.tar.xz -C /tmp
git config --global --add safe.directory /tmp/flutter
export PATH="$PATH:/tmp/flutter/bin"
export FLUTTER_ROOT="/tmp/flutter"

flutter config --enable-web --no-analytics
flutter pub get
flutter build web --release
