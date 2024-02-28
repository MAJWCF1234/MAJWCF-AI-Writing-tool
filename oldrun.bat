@echo off
echo Installing Python...
choco install python3 -y

echo Python installed successfully!
echo Installing pip...
python -m ensurepip --default-pip

echo pip installed successfully!
echo Running sw_with_gui_and_conversational_ai.py...

python sw_with_gui_and_conversational_ai.py

echo Script completed.

