import re
import threading
from pytube import Playlist
from pytube import YouTube
from tqdm import tqdm

# Define a semaphore to limit the number of concurrent threads
semaphore = threading.Semaphore(5)

# Dictionary to store progress bars for each video
progress_bars = {}

def video_downloader(url,directory):
    with semaphore:
        yt = YouTube(url, on_progress_callback=update_progress, on_complete_callback=complete_progress)
        video = yt.streams.get_highest_resolution()
        video.download(directory)

def playlist_downloader(plylst,directory):
    playlist = Playlist(plylst)
    playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")

    threads = []
    for url in playlist.video_urls:
        thread = threading.Thread(target=video_downloader, args=(url,directory,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Download Complete!")

def update_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    title = stream.title
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100

    if title in progress_bars:
        progress_bars[title].update(percentage)
    else:
        progress_bars[title] = tqdm(total=100, desc=title, unit='%', unit_scale=True)
        progress_bars[title].update(percentage)
        
def complete_progress(stream, file_path):
    title = stream.title
    if title in progress_bars:
        progress_bars[title].close()
        del progress_bars[title]


try:
    print("\nWelcome to the Video Downloader!")
    print("1. Download a single video")
    print("2. Download a playlist")
    print("3. Exit")

    choice = input("Choose an option: ")

    if choice == '1':
        link = input("Enter the link of the video you want to download: ")
        directory = input("Enter the path to the download folder: ")
        video_downloader(link, directory)
    elif choice == '2':
        link = input("Enter the link of the playlist you want to download: ")
        directory = input("Enter the path to the download folder: ")
        playlist_downloader(link, directory)
    elif choice == '3':
        print("Thank you for using the Video Downloader!")
        exit()
    else:
        print("Invalid option! Please choose again.")

except Exception as e:
    print(f"An error occurred: {e}")


