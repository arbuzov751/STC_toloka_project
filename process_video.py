#!/usr/bin/env python3


import argparse
import requests
import os
import sys
import glob
import pandas as pd
from tqdm import tqdm
# import cv2
import datetime

sys.path.insert(1, '/home/arbuzov_misha/STC_toloka_project')

import settings


# def modification_date(filename):
#     t = os.stat(filename)[8]
#     #t = os.path.getmtime(filename)
#     return datetime.datetime.fromtimestamp(t)


def process(video_file):
    file = open(video_file, 'rb')
    files = {'video': (video_file, file)}
    proxies = {'http': None, 'https': None}
    r = requests.post('http://127.0.0.1:8903/', files=files, proxies=proxies)
    file.close()
    return r.text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_video_files", help="path to video files")
    args = parser.parse_args()

    # Get all files from directory with recursive
    all_files = glob.glob(f"{args.path_to_video_files}/**/*.*", recursive=True)
    # Get only files from directory
    # all_files = glob.glob(f"{args.path_to_video_files}/*.*")

    # Make directory for good videos
    path_good = args.path_to_video_files + "/good_videos"
    try:
        os.mkdir(path_good)
    except OSError:
        print(f"Создать директорию {path_good} не удалось")
    else:
        print(f"Успешно создана директория {path_good}")

    # Make directory for bad videos
    path_bad = args.path_to_video_files + "/bad_videos"
    try:
        os.mkdir(path_bad)
    except OSError:
        print(f"Создать директорию {path_bad} не удалось")
        print(OSError)
    else:
        print(f"Успешно создана директория {path_bad}")

    db = []
    for file in tqdm(all_files):
        # modify_date = modification_date(file)
        # print(modify_date)
        # print(repr(modify_date))
        file_name = file.split('/')[-1]

        if file_name.split('.')[1] == 'tsv':
            continue

        # replace file
        comment = process(file)
        if comment == '':
            path_to_file = path_good + "/"

            # video resolution check

            # cap = cv2.VideoCapture(file)
            # width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            #
            # if (width < settings.Width) and (height < settings.Height):
            #     comment = f"Слишком маленькое разрешение видео! Должно быть больше {settings.Width}x{settings.Height}"
            # else:
                # os.replace(file, path_to_file + file_name)

            os.replace(file, path_to_file + file_name)
            # json_check = {
            #     "status": "ACCEPTED",
            #     "public_comment": "Все прекрасно! Спасибо за вашу работу!",
            # }
            # requests.patch(settings.URL_API + "assignments/%s" % file_name.split('.')[0], headers=settings.HEADERS, json=json_check)

        if comment != '':
            path_to_file = path_bad + "/"
            os.replace(file, path_to_file + file_name)
            # json_check = {
            #     "status": "REJECTED",
            #     "public_comment": comment,
            # }
            # requests.patch(settings.URL_API + "assignments/%s" % file_name.split('.')[0], headers=settings.HEADERS, json=json_check)
        db.append(
            {
                "filename": file_name,
                "path to file": path_to_file,
                "comment": comment,
            }
        )
    pd.DataFrame(db).to_csv(f"{args.path_to_video_files}/result.tsv", index=False, sep="\t", encoding='utf-8')
