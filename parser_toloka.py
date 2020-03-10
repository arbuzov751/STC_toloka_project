import pandas as pd
import requests
import mimetypes
from pathlib import Path

# import checker


types = [".3g2", ".3gp", ".3gp2", ".3gpp", ".3gpp2",
         ".asf", ".asx", ".avi", ".bin", ".dat", "drv",
         ".f4v", ".flv", ".gtp", ".h264", ".m4v", ".mkv",
         ".mod", ".moov", ".mov", ".mp4", ".mpeg", ".mpg",
         ".mts", ".rm", ".rmvb", ".spl", ".srt", ".stl",
         ".swf", ".ts", ".vcd", ".vid", ".vob", ".webm",
         ".wm", ".wmv", ".yuv"]  # types all popular video files


def get_media_type(filename):
    mime_start = mimetypes.guess_type(filename)[0]
    return mime_start.split('/')[0]


path_to_save_video = r'C:\STC_toloka_project'

# Specify the key to the API, as well as the pool ID of the first and second jobs

# Main work TOLOKA
# TOLOKA_OAUTH_TOKEN = "AgAAAAA5OljPAACtpYsQUstOSEWDs_k09mbI1M4"
# URL_API = "https://toloka.yandex.ru/api/v1/"

# SANDBOX
TOLOKA_OAUTH_TOKEN = "AgAAAAA8qXcxAAIbujGo7DDpoko2ty3hwvHze6Q"
URL_API = "https://sandbox.toloka.yandex.ru/api/v1/"

HEADERS = {
    "Authorization": "OAuth %s" % TOLOKA_OAUTH_TOKEN,
    "Content-Type": "application/JSON",
}

########################### do check with projects ???

# Get the list of pools in the current project.
url_pools = (
        URL_API + "pools?status=OPEN"  # need check for status?
)
POOLS_ID = requests.get(url_pools, headers=HEADERS).json()["items"]
k = 1  # for the convenience of counting the number of pools

for item in POOLS_ID:
    db = []
    pool_id = item['id']

    print(f"{pool_id} {k}")
    k += 1

    # We get a list of all the answers from the i-th pool that are waiting for verification
    url_assignments = (
            URL_API + "assignments/?status=SUBMITTED&pool_id=%s" % pool_id
    )
    submitted_tasks = requests.get(url_assignments, headers=HEADERS).json()["items"]
    # print(submitted_tasks)

    for task in submitted_tasks:
        # print(task)
        try:
            url_file = (
                # URL_API + "attachments/%s" % task['solutions'][0]['output_values']['video'] # main
                    URL_API + "attachments/%s" % task['solutions'][0]['output_values']['photo']  # sandbox
            )
        except:
            continue

        info_file = requests.get(url_file, headers=HEADERS).json()

        # print(info_file)

        file_name = info_file['name']
        print(file_name)

        # checking file on video using shredding
        video = int(info_file['media_type'].split('/')[0] == "video")
        if info_file['media_type'].split('/')[0] == "application":
            extention = Path(file_name)
            extention.suffix.lower()
            if extention in types:
                video = 1

        if task['solutions'][0]['output_values']['gender'] == "муж.":
            gender = "male"
        else:
            gender = "female"

        if video == 1:
            # pass
            file_download = requests.get(url_file + "/download", headers=HEADERS)  # download file with get request
            # open method to open a file on your system and write the contents
            with open((path_to_save_video + r'\%s' % file_name), "wb") as file:
                file.write(file_download.content)

        db.append(
            {
                "pool_id": task['pool_id'],
                "user_id": task['user_id'],
                "beard": task['solutions'][0]['output_values']['beard'],
                "mustache": task['solutions'][0]['output_values']['mustache'],
                "glasses": task['solutions'][0]['output_values']['glasses'],
                "age": task['solutions'][0]['output_values']['age'],
                "photo": task['solutions'][0]['output_values']['photo'],
                "gender": gender,
                "file_name": file_name,
                "media_type": info_file["media_type"],
                "local_path": path_to_save_video,
                "is_video": video,
            }
        )
        # else:
        ############ make loging.info
        #    json_check = {
        #        "status": "REJECTED",
        #        "public_comment": "Загруженный файл не является видео!",
        #    }
        #    requests.patch(URL_API + "assignments/%s" % task['id'], headers=HEADERS, json=json_check)

        # ---------- local file check ----------
        # file_download = requests.get(url_file + "/download", headers=HEADERS)  # download file with get request
        # # open method to open a file on your system and write the contents
        # with open((path_to_save_video + r'\%s' % file_name), "wb") as file:
        #     file.write(file_download.content)
        #
        # if (get_media_type(path_to_save_video + r'\%s' % file_name) == "video"):
        #     db.append(
        #         {
        #             "pool_id": task['pool_id'],
        #             "user_id": task['user_id'],
        #             "beard": task['solutions'][0]['output_values']['beard'],
        #             "mustache": task['solutions'][0]['output_values']['mustache'],
        #             "glasses": task['solutions'][0]['output_values']['glasses'],
        #             "age": task['solutions'][0]['output_values']['age'],
        #             "photo": task['solutions'][0]['output_values']['photo'],
        #             "gender": task['solutions'][0]['output_values']['gender'],
        #             "file_name": file_name,
        #             "media_type": info_file["media_type"],
        #             "local_path": path_to_save_video,
        #         }
        #     )
        # else:
        #     json_check = {
        #         "status": "REJECTED",
        #         "public_comment": "Загруженный файл не является видео!",
        #     }
        #     requests.patch(URL_API + "assignments/%s" %task['id'], headers=HEADERS, json=json_check)

    pd.DataFrame(db).to_csv(f"pool_{pool_id}.tsv", index=False, sep="\t", encoding='utf-8')
