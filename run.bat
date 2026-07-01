@echo off

REM === 読み込むファイル名を指定 ===
set INPUT_FILE=folder_path.txt

REM === ファイルが存在するかチェック ===
if not exist "%INPUT_FILE%" (
    echo [ERROR] %INPUT_FILE% が見つかりません
    echo 処理を中断します
    pause
    exit /b
)

REM === ファイルの中身（フォルダパス）を読み込む ===
set /p FOLDER_PATH=<"%INPUT_FILE%"

REM === 中身が空でないかチェック ===
if "%FOLDER_PATH%"=="" (
    echo [ERROR] %INPUT_FILE% にフォルダパスが書かれていません
    echo 処理を中断します
    pause
    exit /b
)

REM === フォルダが存在するかチェック ===
if not exist "%FOLDER_PATH%" (
    echo [ERROR] フォルダが存在しません: "%FOLDER_PATH%"
    echo 処理を中断します
    pause
    exit /b
)

REM === Python を実行（フォルダパスを引数として渡す） ===
python main.py -d "%FOLDER_PATH%"

