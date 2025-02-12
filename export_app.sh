



# pyinstaller -n "app" --onefile --windowed --clean --icon='files/logo.ico' --add-data="files;files" --add-data="plugins;plugins" --additional-hooks-dir=. --additional-hooks-dir="./plugins" -p ".;./plugins"  --collect-submodules="plugins" ./main.py

pyinstaller -n "LivingPath" --onefile --windowed --clean --icon='files/logo.ico' --add-data="files:files" --additional-hooks-dir="hooks" --collect-all "hyperglot" -p "."   ./main.py
# on unix systems you can write
# files:files 
# (: instead of ;)

# read -rn1 # keep consol open
