# vexilar
A GUI framework for LLM on a Jetson Orin Nano

Basic setup:

python3 -m venv llm_env   #one-time setup

If PyQt6 fails to install via pip:

pip install -r requirements.txt --no-deps --ignore-installed
sudo apt install python3-pyqt6

Running the App:

source llm_env/bin/activate

cd vexilar
python main.py