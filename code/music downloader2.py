from pytube import YouTube, Playlist
from bs4 import BeautifulSoup
import PySimpleGUI as sg
from pathlib import Path
import requests
import os
import re

def get_full_title(video_url):
    try:
        response = requests.get(video_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            full_title = title_tag.text.strip()
            return full_title
    except requests.RequestException as e:
        print(f"Error getting title: {e}")
        return None

def sanitize_filename(filename):
    filename_pattern = re.compile(r'[\\/:"*?<>|]')
    sanitized = filename_pattern.sub('_', filename)
    return sanitized

def delete_webm_files(output_path, window, output_key):
    try:
        webm_files = list(Path(output_path).glob("*.webm"))
        for webm_file in webm_files:
            os.remove(webm_file)
            window[output_key].update(f"\n Deleted {len(webm_file)} .webm files \n")
    except:
        pass

def download_audio(video_url, output_path, window, output_key):
    try:
        yt = YouTube(video_url)
        audio_streams = yt.streams.filter(only_audio=True, file_extension='webm').order_by('abr').desc()
        if audio_streams:
            title = get_full_title(video_url) or "Unknown_Title"
            highest_quality_stream = audio_streams.first()
            highest_quality_stream.download(output_path)
            source_path = Path(output_path) / highest_quality_stream.default_filename
            dest_filename = f"{sanitize_filename(title)}.mp3"
            dest_path = Path(output_path) / dest_filename
            if not dest_path.exists():
                os.rename(source_path, dest_path)
            if output_key == "output_single":
                output_messages_single = f"downloaded successfully: {dest_filename}\n"
                window[output_key].update(output_messages_single)
                delete_webm_files(output_path, window, output_key)
            elif output_key == "output_playlist":
                output_messages_single = f"downloaded successfully: {dest_filename}\n"
                window[output_key].update(output_messages_single)
                delete_webm_files(output_path, window, output_key)
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

def download_playlist_audio(playlist_url, output_path, window, output_key):
    playlist = Playlist(playlist_url)
    for video_url in playlist.video_urls:
        download_audio(video_url, output_path, window, output_key)
        window[output_key].update("The playlist downloads have all been successful.")

def main():
    sg.theme("DefaultNoMoreNagging")
    layout = [
        [sg.Text("Audio Download Tool", font=('bitstream charter', 18, 'bold'))],  
        [sg.Text("Select Folder"),
        sg.Input(key="output_folder", expand_x=True), 
        sg.FolderBrowse(target="output_folder")],
        [sg.TabGroup([
            [sg.Tab('Download Single Video', [
                [sg.Text('Enter YouTube Video URL:'), sg.InputText(key='video_url')],
                [sg.Button('Download', key="d1")],
                [sg.Output(size=(60, 10), key='output_single')]
            ])],
            [sg.Tab('Download Playlist', [
                [sg.Text('Enter YouTube Playlist URL:'), sg.InputText(key='playlist_url')],
                [sg.Button('Download', key="d2")],
                [sg.Output(size=(60, 10), key='output_playlist')]
            ])],
        ])]
    ]
    window = sg.Window("YouTube Downloader", layout, finalize=True, resizable=True)
    output_messages_single, output_messages_playlist = "", ""

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        if event == 'd1' and values['video_url']:
            try:
                output_key = 'output_playlist'
                download_audio(values['video_url'], values["output_folder"], window, "output_single")
                window['video_url'].update('')
            except Exception as e:
                output_messages_single += f"Error downloading: {str(e)}\n"

        if event == 'd2' and values['playlist_url']:
            try:
                output_key = 'output_playlist'
                download_playlist_audio(values['playlist_url'], values["output_folder"], window, "output_playlist")
                window['playlist_url'].update('')
            except Exception as e:
                output_messages_playlist += f"Error downloading: {str(e)}\n"
                window[output_key].update(output_messages_playlist)
    window.close()

if __name__ == "__main__":
    main()