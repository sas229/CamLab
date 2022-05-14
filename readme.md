To build with PyInstaller from Linux:

pipenv run pyinstaller --onefile --clean --noconsole  --add-data "src:." src/main.py

From Windows:

pipenv run pyinstaller --onefile --clean --noconsole --add-data "src;." src/main.py