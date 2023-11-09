import glob
import sqlite3
conn = sqlite3.connect(glob.glob('**/' + 'task_manager.db', recursive=True)[0])
conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY NOT NULL, password TEXT NOT NULL)")
conn.close()
