import pandas as pd
import requests
from pathlib import Path
import settings
import glob
from tqdm import tqdm


HEADERS = {
    "Authorization": "OAuth %s" % settings.TOLOKA_OAUTH_TOKEN,
    "Content-Type": "application/JSON",
}

# Get the list of pools in the current project.

all_files = glob.glob(f"{settings.path_to_save_video}\*.*")

url_pools = (
        settings.URL_API + f"pools/{settings.pool_id}"
)
POOL_ID = requests.get(url_pools, headers=HEADERS).json()

db = []
pool_id = POOL_ID['id']

print(f"{pool_id}")

# We get a list of all the answers from the i-th pool that are waiting for verification
url_assignments = (
        settings.URL_API + "assignments/?status=ACCEPTED&limit=200&pool_id=%s" % pool_id  # set the right amount limit!!!!
)
submitted_tasks = requests.get(url_assignments, headers=HEADERS).json()["items"]

for task in tqdm(submitted_tasks):
    try:
        url_file = (
            #    settings.URL_API + "attachments/%s" % task['solutions'][0]['output_values']['video']  # main
                settings.URL_API + "attachments/%s" % task['solutions'][0]['output_values']['photo']  # sandbox
        )
    except:
        continue

    info_file = requests.get(url_file, headers=HEADERS).json()

    file_name = info_file['name']

    # checking file on video using shredding
    video = int(info_file['media_type'].split('/')[0] == "video")
    if info_file['media_type'].split('/')[0] == "application":
        extention = Path(file_name)
        extention = extention.suffix.lower()
        if extention in settings.types:
            video = 1

    if task['solutions'][0]['output_values']['gender'] == "муж.":
        gender = "male"
    else:
        gender = "female"

    if video == 1:
        if file_name not in all_files:
            # pass
            file_download = requests.get(url_file + "/download", headers=HEADERS)  # download file with get request
            # open method to open a file on your system and write the contents
            with open((settings.path_to_save_video + r'\%s' % file_name), "wb") as file:
                file.write(file_download.content)

    db.append(
        {
            "pool_id": task['pool_id'],
            "user_id": task['user_id'],
            "beard": task['solutions'][0]['output_values']['beard'],
            "mustache": task['solutions'][0]['output_values']['mustache'],
            "glasses": task['solutions'][0]['output_values']['glasses'],
            "age": task['solutions'][0]['output_values']['age'],
            "photo": task['solutions'][0]['output_values']['photo'],  # sandbox
            # "video": task['solutions'][0]['output_values']['video'],
            "gender": gender,
            "file_name": file_name,
            "media_type": info_file["media_type"],
            "local_path": settings.path_to_save_video,
            "is_video": video,
            "md5_hash": 0,
        }
    )
if db:
    pd.DataFrame(db).to_csv(f"pool_{pool_id}.tsv", index=False, sep="\t", encoding='utf-8')
