import PySimpleGUI as sg
from pytube import YouTube, Playlist
from pathlib import Path
import os
import re
import requests
from bs4 import BeautifulSoup

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
    except Exception as e:
        return str(e)

def download_playlist_audio(playlist_url, output_path):
    playlist = Playlist(playlist_url)
    for video_url in playlist.video_urls:
        downloaded_file = download_audio(video_url, output_path)
        if downloaded_file:
            yield downloaded_file

def create_tab_layout():
    tab1 = [
        [sg.InputText(size=(60, 1), key="url_tab1", expand_x=True)],
        [sg.Button("Download", key="download_tab1")],
        [sg.Output(size=(80, 15), key="tab1_output")],
    ]

    tab2 = [
        [sg.InputText(size=(60, 1), key="url_tab2", expand_x=True)],
        [sg.Button("Download", key="download_tab2")],
        [sg.Output(size=(80, 15), key="tab2_output")],
    ]

    tab_group = [
        [sg.TabGroup([
            [sg.Tab('Single Audio', tab1, key="tab1"),    
            sg.Tab('Playlist', tab2, key="tab2")]
        ], key='tab_group')],
    ]
    return tab_group

def main(): 
    sg.theme("DefaultNoMoreNagging")
    layout = [
        [sg.Text("Audio Download Tool", font=('bitstream charter', 18, 'bold'))],  
        [sg.Text("Select Folder"),
        sg.Input(key="output_folder", expand_x=True), 
        sg.FolderBrowse(target="output_folder")],
        [create_tab_layout()],
    ]
    window = sg.Window("Audio Download Tool", layout, finalize=True, resizable=True)
    output_messages = ""

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Exit'):  
            break
        elif event and "download" in event.lower():
            active_tab_key = window['tab_group'].Widget.SelectedKey
            url, output_path = values[f"url_{active_tab_key}"], values["output_folder"]

            if active_tab_key == "tab1":
                downloaded_file = download_audio(url, output_path)
                if downloaded_file:
                    output_messages += f"\n Single Video Audio Downloaded:\n {downloaded_file} \n"

            elif active_tab_key == "tab2":
                downloaded_files = list(download_playlist_audio(url, output_path))
                if downloaded_files:
                    output_messages += f"Playlist Audio Downloaded:  {len(downloaded_files)} files. \n"

            try:
                window[f"{active_tab_key}_output"].update(output_messages)
                output_messages = delete_webm_files(output_path, output_messages)
            except Exception as e:
                print(str(e))

        try:
            output_messages = delete_webm_files(output_path, output_messages)
        except Exception as e:
            print(str(e))

    window.close()

if __name__ == "__main__":
    main()
