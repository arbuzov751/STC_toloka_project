import argparse
import glob
import os
import hashlib
import pandas as pd
import requests
import settings


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_video_files", help="path to video files")
    args = parser.parse_args()
    all_files = glob.glob(f"{args.path_to_video_files}/*.*", recursive=True)

    db = []
    md5_hash = []
    file_name = []

    for file in all_files:
        if file.split("/")[-1].split('.')[1] == 'tsv':
            continue
        md5_hash.append(md5(file))
        file_name.append(file.split("/")[-1])
        db.append(
            {
                "file_name": file.split("/")[-1],
                "local_path": os.path.dirname(file),
                "md5_hash": 0,
                "is_copy": 0,
                "rejected": 0
            }
        )

    pd.DataFrame(db).to_csv(f"{args.path_to_video_files}/antirepeater.tsv", index=False, sep="\t", encoding='utf-8')
    db = pd.read_csv(f"{args.path_to_video_files}/antirepeater.tsv", delimiter='\t')

    copy = []
    rejected = []

    for item in md5_hash:
        if md5_hash.count(item) > 1:
            copy.append(1)
        else:
            copy.append(0)

    db['md5_hash'] = md5_hash
    db['is_copy'] = copy
    db = db.sort_values('md5_hash')

    md5_hash = db['md5_hash'].tolist()
    file_name = db['file_name'].tolist()
    local_path = db['local_path'].tolist()

    for i in range(len(md5_hash)):
        if (i != 1) and (md5_hash[i] == md5_hash[i - 1]):
            rejected.append(1)
            json_check = {
                "status": "REJECTED",
                "public_comment": "Данное видео загружено повторно! Это нарушает правила выполнения задания!",
            }
            requests.patch(settings.URL_API + f"assignments/{file_name[i].split('.')[0]}", headers=settings.HEADERS,
                           json=json_check)
            try:
                os.remove(local_path[i] + "/" + file_name[i])
            except:
                pass
            continue
        rejected.append(0)

    db['rejected'] = rejected

    pd.DataFrame(db).to_csv(f"{args.path_to_video_files}/antirepeater.tsv", index=False, sep="\t", encoding='utf-8')
