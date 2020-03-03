import pandas as pd
import requests
import mimetypes
from pathlib import Path


# import checker


def get_media_type(filename):
    mime_start = mimetypes.guess_type(filename)[0]
    return mime_start.split('/')[0]



path_to_save_video = r'C:\Users\Arbuzov\Desktop\Work_CVT'

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

########################### do check on projects ???

# Get the list of pools in the current project.
url_pools = (
        URL_API + "pools?"
)
POOLS_ID = requests.get(url_pools, headers=HEADERS).json()["items"]
k = 1  # for the convenience of counting the number of pools
db = []
for item in POOLS_ID:
    pool_id = item['id']

    print(pool_id + " %s" % k)
    k += 1

    # We get a list of all the answers from the i-th pool that are waiting for verification
    url_assignments = (
            URL_API + "assignments/?status=SUBMITTED&pool_id=%s" % pool_id
    )
    submitted_tasks = requests.get(url_assignments, headers=HEADERS).json()["items"]
    print(submitted_tasks)

    for task in submitted_tasks:
        print(task)
        try:
            url_file = (
                # URL_API + "attachments/%s" % task['solutions'][0]['output_values']['video'] # main
                URL_API + "attachments/%s" % task['solutions'][0]['output_values']['photo']  # sandbox
            )
        except:
            continue

        info_file = requests.get(url_file, headers=HEADERS).json()

        print(info_file)

        file_name = info_file['name']

        # checking file on video using shredding
        video = (info_file['media_type'].split('/')[0] == "video")

        if task['solutions'][0]['output_values']['gender'] == "муж.":
            gender = "male"
        else:
            gender = "female"

        # file_download = requests.get(url_file + "/download", headers=HEADERS)  # download file with get request
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

pd.DataFrame(db).to_csv("result.tsv", index=False, sep="\t", encoding='utf-8')
