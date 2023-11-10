import unittest
import os
import sys
import shutil
import sqlite3
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Application.data_management import create_database, insert_video, get_all_videos, delete_old_videos

class TestDataManagement(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = 'test_directory'
        
        # Set up a database
        database_path = os.path.join(self.test_dir, 'video_database.db')
        create_database(database_path)

        # Duplicate contents of 'in' and 'out' folders from 'Files' directory to 'test_directory'
        self.duplicate_files_to_test_directory()

    def tearDown(self):
        # Delete the database after each test
        database_path = os.path.join(self.test_dir, 'video_database.db')
        if os.path.exists(database_path):
            os.remove(database_path)

    def duplicate_files_to_test_directory(self):
        # Copy the contents of 'Files/in' to 'test_directory/in'
        files_in_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Files', 'in'))
        test_in_directory = os.path.join(self.test_dir, 'in')

        if not os.path.exists(test_in_directory):
            os.makedirs(test_in_directory)

        for item in os.listdir(files_in_dir):
            s = os.path.join(files_in_dir, item)
            d = os.path.join(test_in_directory, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, False, None)
            else:
                shutil.copy2(s, d)

        # Copy the contents of 'Files/out' to 'test_directory/out'
        files_out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Files', 'out'))
        test_out_directory = os.path.join(self.test_dir, 'out')

        if not os.path.exists(test_out_directory):
            os.makedirs(test_out_directory)

        for item in os.listdir(files_out_dir):
            s = os.path.join(files_out_dir, item)
            d = os.path.join(test_out_directory, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, False, None)
            else:
                shutil.copy2(s, d)


    def test_01_insert_and_retrieve_videos(self):
        # Insert test videos
        database_path = os.path.join(self.test_dir, 'video_database.db')
        insert_video(os.path.join('in_1.mp4'), 'in', database_path=database_path)
        insert_video(os.path.join('out_1.mp4'), 'out', database_path=database_path)

        # Retrieve and check if they are retrieved correctly
        videos = get_all_videos(database_path=database_path)
        print("All Videos after insertion:", videos)
        self.assertEqual(len(videos), 2)

    def test_02_delete_old_videos(self):
        # Insert test videos
        database_path = os.path.join(self.test_dir, 'video_database.db')
        insert_video(os.path.join('in_2.mp4'), 'in', database_path=database_path)
        insert_video(os.path.join('out_2.mp4'), 'out', database_path=database_path)
        
        # Retrieve all videos before deletion
        videos_before_deletion = get_all_videos(database_path=database_path)
        print("All Videos before deletion:", videos_before_deletion)
        # Set the timestamp of one video to be older than 1 day
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        timestamp = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('UPDATE videos SET timestamp = ? WHERE folder = ?', (timestamp, 'in'))
        conn.commit()
        conn.close()

        # Delete old videos and check if the count is reduced
        delete_old_videos(1, database_path=database_path, files_path=self.test_dir)

        # Retrieve all videos after deletion
        videos_after_deletion = get_all_videos(database_path=database_path)
        print("All Videos after deletion:", videos_after_deletion)
        self.assertEqual(len(videos_after_deletion), len(videos_before_deletion) - 1)

if __name__ == '__main__':
    unittest.main()
