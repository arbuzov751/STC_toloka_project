#!/usr/bin/env python3


import argparse
import requests
import os
import sys
import glob
import pandas as pd

sys.path.insert(1, '/home/arbuzov_misha/STC_toloka_project')

import settings

def process(video_file):
    file = open(video_file, 'rb')
    files = {'video': (video_file, file)}
    proxies = {'http': None, 'https': None}
    r = requests.post('http://127.0.0.1:8901/', files=files, proxies=proxies)
    file.close()
    return r.text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_video_files", help="path to video files")
    args = parser.parse_args()

    # Get all files from directory
    all_files = glob.glob(f"{args.path_to_video_files}/*.*")

    # Make directory for good videos
    path_good = args.path_to_video_files+"/good_videos"
    try:
        os.mkdir(path_good)
    except OSError:
        print(f"Создать директорию {path_good} не удалось")
    else:
        print(f"Успешно создана директория {path_good}")

    # Make directory for bad videos
    path_bad = args.path_to_video_files+"/bad_videos"
    try:
        os.mkdir(path_bad)
    except OSError:
        print(f"Создать директорию {path_bad} не удалось")
    else:
        print(f"Успешно создана директория {path_bad}")

    db = []

    for file in all_files:
        file_name = file.split('/')[-1]

        # replace file
        comment = process(file)
        if comment == '':
            path_to_file = path_good + "/"
            os.replace(args.path_to_video_files+"/"+file_name, path_to_file + file_name)
            json_check = {
                "status": "ACCEPTED",
                "public_comment": "Все прекрасно! Спасибо за вашу работу!",
            }
            requests.patch(settings.URL_API + "assignments/%s" % file_name, headers=settings.HEADERS, json=json_check)
        else:
            path_to_file = path_bad+"/"
            os.replace(args.path_to_video_files+"/"+file_name, path_to_file + file_name)
            json_check = {
                "status": "REJECTED",
                "public_comment": "На видео отсутствует лицо! Либо оно перекрыто чем-то или пропадает!",
            }
            requests.patch(settings.URL_API + "assignments/%s" % file_name, headers=settings.HEADERS, json=json_check)
        db.append(
            {
                "filename": file_name,
                "path to file": path_to_file,
                "comment": comment,
            }
        )

    if db:
        pd.DataFrame(db).to_csv(f"{args.path_to_video_files}/result.tsv", index=False, sep="\t", encoding='utf-8')
