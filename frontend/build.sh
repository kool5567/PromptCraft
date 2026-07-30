#!/bin/bash
set -e

echo "Installing Flutter stable..."
git clone --depth 1 --branch stable --single-branch https://github.com/flutter/flutter.git /tmp/flutter 2>&1

export PATH="$PATH:/tmp/flutter/bin"
export FLUTTER_ROOT="/tmp/flutter"

flutter config --enable-web --no-analytics
flutter create --platforms web .
flutter pub get
flutter build web --release
