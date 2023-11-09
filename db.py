import os
import sqlite3
conn = sqlite3.connect(os.path.abspath("dist/task_manager.db"))
conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY NOT NULL, password TEXT NOT NULL)")
conn.close()
