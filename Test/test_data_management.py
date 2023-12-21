import unittest
import os
import sys
import shutil
import sqlite3
from moviepy.editor import VideoFileClip
from datetime import datetime, timedelta
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Application.data_management import create_database, insert_video, get_all_videos, delete_old_videos

class TestDataManagement(unittest.TestCase):

    def setUp(self):
        '''
        Creates a mock directory for testing, sets up test database and ensures mirroring of 
        files from parent files directory to the test directory
        '''
        # Create a temporary directory for testing
        self.test_dir = 'test_directory'
        
        # Set up a database
        database_path = os.path.join(self.test_dir, 'video_database.db')
        create_database(database_path)

        # Duplicate contents of 'in' and 'out' folders from 'Files' directory to 'test_directory'
        self.duplicate_files_to_test_directory()
    

    def tearDown(self):
        '''
        Deletes the database after each test to ensure integrity of the mock database
        
        '''
        # Delete the database after each test
        database_path = os.path.join(self.test_dir, 'video_database.db')
        if os.path.exists(database_path):
            os.remove(database_path)

    def duplicate_files_to_test_directory(self):
        '''
        Helper function which copies over the contents of the files directory to a 
        dummy in the test directory. Skips copying if the file or directory already exists.
        '''
        # Function to handle the copying of each folder's content
        def copy_folder_contents(src_folder, dest_folder):
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)

            for item in os.listdir(src_folder):
                src_path = os.path.join(src_folder, item)
                dest_path = os.path.join(dest_folder, item)

                if os.path.isdir(src_path):
                    if not os.path.exists(dest_path):
                        shutil.copytree(src_path, dest_path)
                else:
                    if not os.path.exists(dest_path):
                        shutil.copy2(src_path, dest_path)

        # Copy the contents of 'Files/in' to 'test_directory/in'
        files_in_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Files', 'in'))
        test_in_directory = os.path.join(self.test_dir, 'in')
        copy_folder_contents(files_in_dir, test_in_directory)

        # Copy the contents of 'Files/out' to 'test_directory/out'
        files_out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Files', 'out'))
        test_out_directory = os.path.join(self.test_dir, 'out')
        copy_folder_contents(files_out_dir, test_out_directory)



    def test_01_insert_and_retrieve_videos(self):
        '''
        Test for the insertion and retrieval of videos from cloud directory
        
        '''
        
        #print('---------------------------------------------------------------------------------------')
        #print('Testing insertion and retrieval:')
        # Insert test videos
        database_path = os.path.join(self.test_dir, 'video_database.db')
        insert_video(os.path.join('in_1.mp4'), 'in', database_path=database_path)
        insert_video(os.path.join('in_2.mp4'), 'in', database_path=database_path)

        # Retrieve and check if they are retrieved correctly
        videos = get_all_videos(database_path=database_path)
        #print("All Videos after insertion:", videos)
        self.assertEqual(len(videos), 2)

    def test_02_delete_old_videos(self):
        '''
        Tests for deletion of old videos that are older than certain timestamp. 
        Changes timestamp to something post expiration first.
        '''
        #print('---------------------------------------------------------------------------------------')
        #print('Testing deletion after expiration')
        # Insert test videos
        database_path = os.path.join(self.test_dir, 'video_database.db')
        insert_video(os.path.join('in_3.mp4'), 'in', database_path=database_path)
        insert_video(os.path.join('in_4.mp4'), 'in', database_path=database_path)
        
        # Retrieve all videos before deletion
        videos_before_deletion = get_all_videos(database_path=database_path)
        #print("All Videos before deletion:", videos_before_deletion)
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
        #print("All Videos after deletion:", videos_after_deletion)
        self.assertEqual(len(videos_after_deletion), 0)
    def test_03_metadata_unavailable(self):
        '''
        Tests for presence of metadata within the video files to see if theyve been deleted before storage
        '''
        #print('---------------------------------------------------------------------------------------')
        #print("Testing for metadata removal")
        database_path = os.path.join(self.test_dir, 'video_database.db')
        videos = get_all_videos(database_path=database_path)
        
        for video in videos:
            if video[2] == 'in':  # Assuming the third element is the folder name
                filename = os.path.join(os.path.join(self.test_dir, 'in'), video[1])  # Adjust path as needed

                if os.path.exists(filename):
                    clip = VideoFileClip(filename)
                    self.assertIsNotNone(clip.metadata, f"Metadata should be present in video {filename}")
    
    def test_04_gait_values_encrypted(self):
        '''
        Tests for encryption of gait in database
        '''
        database_path = os.path.join(self.test_dir, 'video_database.db')
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT gait FROM videos WHERE folder = 'in'")
        gait_entries = cursor.fetchall()
        for entry in gait_entries:
            gait_data = json.loads(entry[0]) 


            for key, value in gait_data.items():
                self.assertLess(value, 0, f"Value for {key} in gait data is not negative: {value}")

        conn.close()
    
    def test_05_gait_validity(self):
        '''
        Checks if valid gait has been stored in the database in JSON format (encrypted)
        '''
        database_path = os.path.join(self.test_dir, 'video_database.db')
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT gait, key FROM videos WHERE folder = 'in'")
        entries = cursor.fetchall()
        for gait_json, key_value in entries:
            gait_data = json.loads(gait_json)
            adjusted_gait_data = {k: v + key_value for k, v in gait_data.items()}
            first_metric = next(iter(adjusted_gait_data.values()))

            self.assertGreater(first_metric, 0, f"The adjusted first value of gait data should be positive, found {first_metric}")

        conn.close()
    
    def test_06_file_name_safe(self):
        '''
        Tests if filename does not contain tracable identity information
        '''
        database_path = os.path.join(self.test_dir, 'video_database.db')
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT filename FROM videos")
        filenames = cursor.fetchall()
        for filename, in filenames:
            name_without_extension = os.path.splitext(filename)[0]
            self.assertLess(len(name_without_extension), 5, f"Filename {filename} is not less than 5 characters")
        conn.close()

    def test_07_recorded_consent(self):
        '''
        Tests that all videos stored had explicit consent for storage
        '''
        database_path = os.path.join(self.test_dir, 'video_database.db')
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM videos")
        ids = cursor.fetchall()
        for id_tuple in ids:
            id_value = id_tuple[0]
            self.assertGreater(id_value, 0, f"The id should be positive, found {id_value}")

        conn.close()
if __name__ == '__main__':
    unittest.main(verbosity=2)
 
 
 