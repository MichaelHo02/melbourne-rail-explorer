#!/bin/sh
set -eu
# Run from the repository root after build_train.py. Door nodes must stay separate.
for asset in melbourne-commuter driver-cab; do
  npx --yes @gltf-transform/cli@4.5.0 optimize "public/models/$asset.glb" "/tmp/$asset-optimized.glb" \
    --compress false --flatten false --join false --instance false --palette false --simplify-error 0.00005
  cp "/tmp/$asset-optimized.glb" "public/models/$asset.glb"
done
