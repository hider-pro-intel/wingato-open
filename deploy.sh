#!/usr/bin/env bash
# Push Wingato Open to your GitHub repo (create an EMPTY repo first).
set -e
cd "$(dirname "$0")"

if [ ! -d .git ]; then
  git init
  git branch -M main
fi

git add .
git commit -m "Wingato Open" || true

echo
echo "Paste your GitHub repo URL, e.g. https://github.com/you/wingato-open.git"
read -r REMOTE

git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"
git push -u origin main

echo
echo "Pushed. Now: render.com -> New + -> Blueprint -> pick this repo."
