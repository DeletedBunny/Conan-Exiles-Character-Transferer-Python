import sqlite3
from tkinter import *
import DatabaseHelper
import UiCharacterTransferer

#Database initialization/connection area
print('DB Init...')
exilesDbConnection = sqlite3.connect('game.db')
exilesCursor = exilesDbConnection.cursor()
siptahDbConnection = sqlite3.connect('dlc_siptah.db')
siptahCursor = siptahDbConnection.cursor()
databaseHelper = DatabaseHelper.DatabaseHelper(exilesCursor, siptahCursor, exilesDbConnection, siptahDbConnection)
print('DB Connected')

#UI initialization area
print('UI Init...')
uiRoot = Tk()
uiMain = UiCharacterTransferer.UiCharacterTransferer(uiRoot, databaseHelper)
uiMain.init_common_components()
uiMain.switch_page()
print('UI Started')

uiRoot.mainloop()