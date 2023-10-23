import PySimpleGUI as sg
from pytube import YouTube, Playlist
import os
import re
import requests
from pathlib import Path
from bs4 import BeautifulSoup

# Function to retrieve the full title of a YouTube video
def get_full_title(video_url):
    try:
        response = requests.get(video_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            full_title = title_tag.text.strip()
            return full_title
    except:
        pass

def sanitize_filename(filename):
    filename_pattern = re.compile(r'[\\/:"*?<>|]')
    sanitized = filename_pattern.sub('_', filename)
    return sanitized

def delete_webm_files(output_path, output_messages):
    try:
        webm_files = list(Path(output_path).glob("*.webm"))
        for webm_file in webm_files:
            os.remove(webm_file)
        output_messages += f"\n Deleted {len(webm_files)} .webm files \n"
        return output_messages
    except:
        pass

# Function to download audio from a YouTube video and optionally convert it to MP3
def download_audio(video_url, output_path):
    try:
        yt = YouTube(video_url)
        audio_streams = yt.streams.filter(only_audio=True, file_extension='webm').order_by('abr').desc()
        if audio_streams:
            title = get_full_title(video_url)
            highest_quality_stream = audio_streams.first()
            highest_quality_stream.download(output_path)
            source_path = Path(output_path) / highest_quality_stream.default_filename
            dest_filename = f"{sanitize_filename(title)}.mp3"
            dest_path = Path(output_path) / dest_filename
            if not dest_path.exists():
                os.rename(source_path, dest_path)
            return dest_filename
    except:
        pass

# Generator function to download audio from a YouTube playlist
def download_playlist_audio(playlist_url, output_path):
    playlist = Playlist(playlist_url)
    for video_url in playlist.video_urls:
        downloaded_file = download_audio(video_url, output_path)
        if downloaded_file:
            yield downloaded_file

# Main GUI application
def main(): 
    font_title = "bitstream charter"
    font_button = "bitstream charter"#"courier 10 pitch"
    InputText_w = 51
    sg.theme("DefaultNoMoreNagging")
    layout = [
        [sg.Text("Audio Download Tool", font=(font_title, 18,"bold"))],
        [sg.Text("Enter Video URL or Playlist URL：",font=(font_title,14))],
        [sg.InputText(key="url_input", size=(InputText_w, 1))],
        [sg.Text("Select Download Path：", font=(font_title, 14))],
        [sg.InputText(key="output_path", size=(InputText_w, 1)), 
            sg.FolderBrowse(target="output_path", font=(font_button, 10, "bold") )],
        [sg.Button("Download Single Video", font=(font_button, 12,"bold")), 
            sg.Button("Download Playlist", font=(font_button, 12,"bold")), 
            sg.Button("Exit", font=(font_button, 12,"bold")), ],
        [sg.Multiline("", key="-output-", size=(62, 10), disabled=True, expand_y=True)]
    ]
    window = sg.Window("Audio Download Tool", layout, resizable=True, icon="../images/music_icon.png", finalize=True)
    window.set_min_size((470,450) )
    output_messages = ""
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Exit":
            break
        elif event == "Download Single Video":
            video_url = values["url_input"]
            output_path = values["output_path"]
            downloaded_file = download_audio(video_url, output_path)
            if downloaded_file:
                output_messages += f"\n Single Video Audio Downloaded:\n {downloaded_file} \n"
        elif event == "Download Playlist":
            playlist_url = values["url_input"]
            output_path = values["output_path"]
            downloaded_files = list(download_playlist_audio(playlist_url, output_path))
            if downloaded_files:
                # output_messages += f"Playlist Audio Downloaded: \n {', '.join(downloaded_files)}\n"
                output_messages += f"Playlist Audio Downloaded:  {len(downloaded_files)} files. \n"

        try:
            output_messages = delete_webm_files(output_path, output_messages)
            window["-output-"].update(value=output_messages)
        except:
            pass
    window.close()

if __name__ == "__main__":
    main()
