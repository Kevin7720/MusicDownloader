import sys
import music_layout

if __name__ == "__main__":
    sys.stdout = open('log.txt', 'w') 
    sys.stderr = sys.stdout
    music_layout.bulid_layout()
