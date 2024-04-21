# Installation Guide

## Install and Run Server/Web Tool

### Python and Scoop Setup
1. Install Python 3.11.6 and ensure to check "Add Python to PATH":
    - Download Python 3.11.6 from the official [Python website](https://www.python.org/downloads/).
    - During the installation, make sure to select the option to add Python to your system's PATH.

2. Install Scoop and required tools using PowerShell:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    irm get.scoop.sh | iex
    scoop install ffmpeg
    scoop install git
    ```

### Clone and Setup Pure Blur
1. Download the Pure Blur repository:
    ```powershell
    git clone https://github.com/paco1127/Pure-Blur.git
    ```

2. Change directory to Pure Blur source code:
    ```powershell
    cd Pure-Blur
    ```

3. Run the start script:
    ```powershell
    ./start.bat
    ```

## Install Web Extension

### Setup Git and Clone Repository
1. Install Git using Scoop and set up the execution policy in PowerShell:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    irm get.scoop.sh | iex
    scoop install git
    ```

2. Clone the Pure Blur repository:
    ```powershell
    git clone https://github.com/paco1127/Pure-Blur.git
    ```

### Load Extension in Google Chrome
1. Open Google Chrome and navigate to the "Extensions" tab.
2. Enable "Developer mode" by toggling the switch in the top right corner.
3. Click on "Load unpacked".
4. Navigate to the `Pure Blur Extension` folder within the cloned repository and select it.
5. Click "Choose folder" to load the extension into Chrome.

The extension will now be available in your browser.


For a Traditional Chinese version of this guide, please [click here](#README(ch).md).
