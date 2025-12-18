To install using pip:

- Install LJM (https://files.labjack.com/installers/LJM/Windows/x86_64/release/LabJack_2025-05-07.exe)
- Install Python 3.11.4 (https://www.python.org/downloads/latest/pymanager/)
- Run the following commands:

git clone https://github.com/sas229/CamLab.git

cd CamLab

py -3.11 -m venv venv

venv\Scripts\activate

pip install .

python src/main.py
