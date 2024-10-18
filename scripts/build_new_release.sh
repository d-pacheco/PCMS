#!/bin/bash

# Install required Python packages
pip install -r requirements-base.txt
pip install -r requirements-dev.txt

# Run PyInstaller to create a standalone executable
python -m PyInstaller -F main_gui.py -n 'PCMS'

# Check if PyInstaller ran successfully
if [ $? -eq 0 ]; then
    # Delete the build folder
    rm -rf build

    # Delete the spec file
    rm -f PCMS.spec

    # Move the executable out of the dist folder
    mv dist/PCMS.exe .

    # Delete the dist folder
    rm -rf dist

    echo "Build process completed successfully."
else
    echo "PyInstaller encountered an error."
fi
