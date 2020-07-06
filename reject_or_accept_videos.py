import glob
import requests
import settings
import argparse
from tqdm import tqdm
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_videos", help="path to videos")
    parser.add_argument("reject_or_accept", help="switch between reject and accept files")
    args = parser.parse_args()
    all_files = glob.glob(f"{args.path_to_videos}/*.*")

    for file in tqdm(all_files):
        file_name = file.split('/')[-1]
        if file_name.split('.')[1] == 'tsv':
            continue
        if args.reject_or_accept.lower() == "reject":
            json_check = {
                "status": "REJECTED",
                "public_comment": "Видео не соответствует требованиям, указанным в инструкции",
            }
            requests.patch(settings.URL_API + "assignments/%s" % file_name.split('.')[0], headers=settings.HEADERS, json=json_check)
            try:
                os.remove(file)
            except:
                print(f"Не удалось удалить видео {file_name}")
        elif args.reject_or_accept.lower() == "accept":
            json_check = {
                "status": "ACCEPTED",
                "public_comment": "Все прекрасно! Спасибо за вашу работу!",
            }
            requests.patch(settings.URL_API + "assignments/%s" % file_name.split('.')[0], headers=settings.HEADERS, json=json_check)
        else:
            print("You entered the wrong parameter. Need enter reject or accept!")
            break
