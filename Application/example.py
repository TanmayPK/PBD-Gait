from data_management import create_database, insert_video, delete_old_videos, get_all_videos
import os 
from datetime import datetime, timedelta

def get_video_files(folder):
    folder_path = os.path.join('..', 'Files', folder)
    videos = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
    return videos

# Example usage
database_path = 'video_database.db'

# Delete the database file if it exists
if os.path.exists(database_path):
    os.remove(database_path)

create_database()

# Assuming you have a list of video files in the 'in' and 'out' folders
in_folder_path = 'in'
out_folder_path = 'out'

in_folder_videos = get_video_files(in_folder_path)
# out_folder_videos = get_video_files(out_folder_path)

# Insert videos with timestamps older than 7 days for testing purposes
older_than_7_days = datetime.now() - timedelta(days=10)

for video in in_folder_videos:
    insert_video(video, 'in', timestamp=older_than_7_days.strftime('%Y-%m-%d %H:%M:%S'))

# Retrieve all videos from the database
all_videos = get_all_videos()
print("All Videos:")
for video in all_videos:
    print(video)

# Delete videos older than 7 days
delete_old_videos(7)
print("\nVideos after deleting old ones:")
all_videos = get_all_videos()
for video in all_videos:
    print(video)
