



# pyinstaller -n "app" --onefile --windowed --clean --icon='files/logo.ico' --add-data="files;files" --add-data="plugins;plugins" --additional-hooks-dir=. --additional-hooks-dir="./plugins" -p ".;./plugins"  --collect-submodules="plugins" ./main.py

pyinstaller -n "app" --onefile --windowed --clean --icon='files/logo.ico' --add-data="files;files" --additional-hooks-dir="hooks" -p "."   ./main.py

# read -rn1 # keep consol open
