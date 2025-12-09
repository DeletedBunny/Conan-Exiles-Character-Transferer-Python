import os
import shutil
import sqlite3
from tkinter import *
import DatabaseHelper
import UiCharacterTransferer

# Setup work area, backups, etc
print('Setup...')
if not os.path.exists('Backup'):
    print('Creating backup folder...')
    os.mkdir('Backup')
print('Cleaning backup folder...')
for filename in os.listdir('Backup'):
    file_path = os.path.join('Backup', filename)
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
    except Exception as e:
        print('Failed to delete ' + str(file_path) + '. Error: ' + str(e))
        os._exit(0)

if not os.path.exists('game.db') or not os.path.exists('dlc_siptah.db'):
    print('Game/DLC databases not found, exiting...')
    os._exit(0)
shutil.copy('game.db', 'Backup/game.db')
shutil.copy('dlc_siptah.db', 'Backup/dlc_siptah.db')
print('Setup complete')

# Database initialization/connection area
print('DB Init...')
exilesDbConnection = sqlite3.connect('game.db')
exilesCursor = exilesDbConnection.cursor()
siptahDbConnection = sqlite3.connect('dlc_siptah.db')
siptahCursor = siptahDbConnection.cursor()
databaseHelper = DatabaseHelper.DatabaseHelper(exilesCursor, siptahCursor, exilesDbConnection, siptahDbConnection)
print('DB Connected')

# UI initialization area
print('UI Init...')
uiRoot = Tk()
uiMain = UiCharacterTransferer.UiCharacterTransferer(uiRoot, databaseHelper)
uiMain.init_common_components()
uiMain.switch_page()
print('UI Started')

uiRoot.mainloop()