pyinstaller ^
--onefile ^
--windowed ^
--clean ^
--noconfirm ^
--add-binary "libs/ffmpeg.exe;libs" ^
--add-binary "libs/ffprobe.exe;libs" ^
--add-data "libs/large-v3-turbo.pt;libs" ^
--name=Offline_Subtitle_Generator ^
--collect-data=whisper ^
ui.py