import PySimpleGUI as sg
from download_audio import *

# GUI application
def bulid_layout(): 
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
    # In winwos system is not working, can't get the right /path.
    # C:\Users\Kevin\AppData\Local\Temp\_MEI170962\music_icon.png False
    # False
    # image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)).replace("code","images"), "music_icon.png")
    # print(image_path, os.path.exists(image_path))
    # print(os.path.isfile(image_path))
    # window = sg.Window("Audio Download Tool", layout, resizable=True, icon=image_path, finalize=True)
    window = sg.Window("Audio Download Tool", layout, resizable=True, finalize=True)
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
            # output_messages = delete_webm_files(output_path, output_messages)
            # window["-output-"].update(value=output_messages)
            pass
        except:
            pass
    window.close()