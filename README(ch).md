# 安裝指南

## 安裝和運行伺服器/網絡工具

### Python 和 Scoop 設定
1. 安裝 Python 3.11.6，並確保選擇 "將 Python 加入 PATH"：
    - 從官方 [Python 網站](https://www.python.org/downloads/) 下載 Python 3.11.6。
    - 安裝時，請確保選擇加入系統 PATH 的選項。

2. 使用 PowerShell 安裝 Scoop 及所需工具：
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    irm get.scoop.sh | iex
    scoop install ffmpeg
    scoop install git
    ```

### 克隆和設置 Pure Blur
1. 下載 Pure Blur 儲存庫：
    ```powershell
    git clone https://github.com/paco1127/Pure-Blur.git
    ```

2. 更改至 Pure Blur 源代碼目錄：
    ```powershell
    cd Pure-Blur
    ```

3. 運行啟動腳本：
    ```powershell
    ./start.bat
    ```

## 安裝網頁擴展

### 設置 Git 和克隆儲存庫
1. 使用 Scoop 安裝 Git 並在 PowerShell 中設定執行政策：
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    irm get.scoop.sh | iex
    scoop install git
    ```

2. 克隆 Pure Blur 儲存庫：
    ```powershell
    git clone https://github.com/paco1127/Pure-Blur.git
    ```

### 在 Google Chrome 中載入擴展
1. 打開 Google Chrome，導航至“擴展功能”選項卡。
2. 啟用“開發者模式”，通過在右上角切換開關。
3. 點擊“載入未封裝項目”。
4. 導航至已克隆儲存庫中的 `Pure Blur Extension` 文件夾並選擇它。
5. 點擊“選擇文件夾”以載入擴展至 Chrome。

擴展將可在您的瀏覽器中使用。
