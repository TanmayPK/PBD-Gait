import sqlite3
import os
from datetime import datetime, timedelta

# Function to create a database and table if they don't exist
def create_database(database_path='video_database.db'):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            folder TEXT,
            timestamp DATETIME
        )
    ''')

    conn.commit()
    conn.close()

# Function to insert a video record into the database
def insert_video(filename, folder, timestamp=None, database_path='video_database.db'):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    if timestamp is None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        INSERT INTO videos (filename, folder, timestamp)
        VALUES (?, ?, ?)
    ''', (filename, folder, timestamp))

    conn.commit()
    conn.close()

# Function to retrieve all videos from the database
def get_all_videos(database_path='video_database.db'):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM videos')
    videos = cursor.fetchall()

    conn.close()

    return videos

def delete_old_videos(days_threshold, database_path='video_database.db', files_path='..\\Files'):
    print("Deleting old videos...")
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    threshold_date = (datetime.now() - timedelta(days=days_threshold)).strftime('%Y-%m-%d %H:%M:%S')

    # Retrieve video records older than the threshold date
    cursor.execute('SELECT filename, folder FROM videos WHERE timestamp < ?', (threshold_date,))
    videos_to_delete = cursor.fetchall()

    # Delete records from the database
    cursor.execute('DELETE FROM videos WHERE timestamp < ?', (threshold_date,))
    conn.commit()
    conn.close()

    # Delete associated video files
    for filename, folder in videos_to_delete:
        file_path = os.path.join(files_path, folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        else:
            print(f"File not found: {file_path}")
