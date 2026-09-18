#!/bin/sh
set -eu

# Vite's test worker treats ':' in the project directory as a URL scheme.
tmp="$(mktemp -d)/frontend"
trap 'rm -rf "$(dirname "$tmp")"' EXIT
mkdir -p "$tmp"
cp -R src index.html package.json tsconfig.json tsconfig.app.json vite.config.ts "$tmp/"
ln -s "$(pwd)/node_modules" "$tmp/node_modules"
cd "$tmp"
node node_modules/vitest/vitest.mjs run
