#!/bin/bash

echo "Checking if pip is already installed..."
if command -v pip3 &>/dev/null; then
    echo "pip is already installed"
    pip3 --version
    exit 0
fi

# Check if python3 is installed
if ! command -v python3 &>/dev/null; then
    echo "Python 3 is not installed. Installing Python 3..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if ! command -v brew &>/dev/null; then
            echo "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install python3
    else
        echo "Please install Python 3 manually for your operating system"
        exit 1
    fi
fi

echo "Downloading get-pip.py..."
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

echo "Installing pip..."
python3 get-pip.py

# Clean up
rm get-pip.py

echo "Verifying pip installation..."
pip3 --version

if [ $? -eq 0 ]; then
    echo "pip was successfully installed!"
    # Create symlink from pip3 to pip
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sudo ln -s $(which pip3) /usr/local/bin/pip
        echo "Created symlink from pip3 to pip"
    fi
else
    echo "There was an error installing pip"
fi