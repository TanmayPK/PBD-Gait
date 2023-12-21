import sqlite3
import os
from datetime import datetime, timedelta
import random
import json

# Function to create a database and table if they don't exist
def create_database(database_path='video_database.db'):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            folder TEXT,
            timestamp DATETIME,
            gait TEXT,
            key INTEGER
        )
        ''')


    conn.commit()
    conn.close()

# Function to insert a video record into the database
import sqlite3
import json
import random
import os
from datetime import datetime

def insert_video(filename, folder, timestamp=None, database_path='video_database.db'):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    if timestamp is None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    gait_data = None
    if folder == 'in':
        json_path = os.path.join('..', 'Files', 'out', filename.replace('.mp4', '.json'))
        if os.path.exists(json_path):
            with open(json_path, 'r') as json_file:
                gait_data = json.load(json_file)

    # Generate large negative number
    key_value = random.randint(-5000, -1000)

    # Add key value to each value in gait data
    if isinstance(gait_data, dict):
        for key in gait_data:
            gait_data[key] += key_value

    # Insert into database
    cursor.execute('''
        INSERT INTO videos (filename, folder, timestamp, gait, key)
        VALUES (?, ?, ?, ?, ?)
    ''', (filename, folder, timestamp, json.dumps(gait_data), key_value))

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
    #print("Deleting old videos...")
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
            #print(f"Deleted file: {file_path}")
        else:
            print(f"File not found: {file_path}")
