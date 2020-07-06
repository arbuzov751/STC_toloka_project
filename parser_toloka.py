import pandas as pd
import requests
import mimetypes
from pathlib import Path
import settings
import glob
import os
from antirepeater import antireplay
from tqdm import tqdm


def get_media_type(filename):
    mime_start = mimetypes.guess_type(filename)[0]
    return mime_start.split('/')[0]


# Get the list of pools in the current project.

POOLS_ID = []

all_files = glob.glob(f"{settings.path_to_save_video}/*.*")

if settings.pool_id == -1:
    url_pools = (
            settings.URL_API + "pools?status=OPEN"
    )
    POOLS_ID = requests.get(url_pools, headers=settings.HEADERS).json()["items"]
else:
    url_pools = (
            settings.URL_API + f"pools/{settings.pool_id}"
    )
    POOL_ID = requests.get(url_pools, headers=settings.HEADERS).json()
    POOLS_ID.append(POOL_ID)  # necessary for the correct operation of the cycle with 1 pool

if POOLS_ID:
    if not os.path.exists(settings.path_to_save_video):
        os.makedirs(settings.path_to_save_video)

for item in POOLS_ID:
    pool_id = item['id']

    print(f"{pool_id}")

    # We get a list of all the answers from the i-th pool that are waiting for verification
    url_assignments = (
            settings.URL_API + "assignments/?status=SUBMITTED&limit=5000&pool_id=%s" % pool_id
    )
    submitted_tasks = requests.get(url_assignments, headers=settings.HEADERS).json()["items"]

    db = []

    for task in tqdm(submitted_tasks):

        try:
            url_file = (
                    settings.URL_API + "attachments/%s" % task['solutions'][0]['output_values']['video']  # main
                #    settings.URL_API + "attachments/%s" % task['solutions'][0]['output_values']['photo']  # sandbox
            )
        except:
            continue

        info_file = requests.get(url_file, headers=settings.HEADERS).json()

        file_name = info_file['name']
        extention = Path(file_name)
        extention = extention.suffix.lower()

        # checking file on video using shredding
        video = int(info_file['media_type'].split('/')[0] == "video")
        if info_file['media_type'].split('/')[0] == "application":
            if extention in settings.types:
                video = 1

        file_name = task['id'] + extention

        if task['solutions'][0]['output_values']['gender'] == "муж.":
            gender = "male"
        else:
            gender = "female"

        local_path = ""
        if video == 1:
            local_path = settings.path_to_save_video
            if (local_path + "/" + file_name not in all_files) and (local_path + "/good_videos/" + file_name not in all_files) \
                    and (local_path + "/bad_videos/" + file_name not in all_files):
                # pass
                file_download = requests.get(url_file + "/download", headers=settings.HEADERS)  # download file with get request
                # open method to open a file on your system and write the contents
                with open((settings.path_to_save_video + r'/%s' % file_name), "wb") as file:
                    file.write(file_download.content)
        elif task['status'] == "SUBMITTED":
            json_check = {
                "status": "REJECTED",
                "public_comment": "Загруженный файл не является видео!",
            }
            requests.patch(settings.URL_API + "assignments/%s" % task['id'], headers=settings.HEADERS, json=json_check)

        db.append(
            {
                "pool_id": task['pool_id'],
                "task_id": task['id'],
                "user_id": task['user_id'],
                "beard": task['solutions'][0]['output_values']['beard'],
                "mustache": task['solutions'][0]['output_values']['mustache'],
                "glasses": task['solutions'][0]['output_values']['glasses'],
                "age": task['solutions'][0]['output_values']['age'],
                # "photo": task['solutions'][0]['output_values']['photo'],  # sandbox
                "video": task['solutions'][0]['output_values']['video'],  # main
                "gender": gender,
                "file_name": file_name,
                "media_type": info_file["media_type"],
                "local_path": local_path,
                "is_video": video,
            }
        )
    if db:
        pd.DataFrame(db).to_csv(f"{settings.path_to_save_video}/pool_{pool_id}.tsv", index=False, sep="\t",
                                    encoding='utf-8')

antireplay()
