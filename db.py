import os
import sqlite3

path = os.path.abspath("dist/task_manager.db")
path = path.replace('\\', '/')
if 'dist/dist/' in path:
    path = path.replace('dist/dist/', 'dist/')

conn = sqlite3.connect(path)
conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY NOT NULL, password TEXT NOT NULL)")
conn.close()
