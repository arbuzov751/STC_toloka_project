# This is settings file!

path_to_save_video = r'/media/hdd/arbuzov_data/toloka_july_2020'

# Specify the key to the API, as well as the pool ID of the first and second jobs

# Main work TOLOKA
TOLOKA_OAUTH_TOKEN = "AgAAAAA5OljPAACtpYsQUstOSEWDs_k09mbI1M4"
URL_API = "https://toloka.yandex.ru/api/v1/"

# SANDBOX
# TOLOKA_OAUTH_TOKEN = "AgAAAAA8qXcxAAIbujGo7DDpoko2ty3hwvHze6Q"
# URL_API = "https://sandbox.toloka.yandex.ru/api/v1/"

HEADERS = {
    "Authorization": "OAuth %s" % TOLOKA_OAUTH_TOKEN,
    "Content-Type": "application/JSON",
}

types = [".3g2", ".3gp", ".3gp2", ".3gpp", ".3gpp2",
         ".asf", ".asx", ".avi", ".bin", ".dat", ".drv",
         ".f4v", ".flv", ".gtp", ".h264", ".m4v", ".mkv",
         ".mod", ".moov", ".mov", ".mp4", ".mpeg", ".mpg",
         ".mts", ".rm", ".rmvb", ".spl", ".srt", ".stl",
         ".swf", ".ts", ".vcd", ".vid", ".vob", ".webm",
         ".wm", ".wmv", ".yuv"]  # types all popular video files

pool_id = 405154  # -1 - поиск по всем открытым пулам

Width, Height = [640, 480]
