#!/bin/sh


# MACOS need conda install -c conda-forge lightgbm
source livingpath/bin/activate
pyinstaller -n "LivingPath" --noconfirm --windowed --icon='files/logo.icns' --add-data="files:files" --additional-hooks-dir="hooks" --collect-all "hyperglot" -p "." ./main.py

# read -rn1 # keep consol open
