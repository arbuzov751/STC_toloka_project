import settings
import hashlib
import os
import pandas as pd
import requests
import numpy as np

HEADERS = {
    "Authorization": "OAuth %s" % settings.TOLOKA_OAUTH_TOKEN,
    "Content-Type": "application/JSON",
}

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


db = pd.read_csv(f"pool_{settings.pool_id}.tsv", delimiter='\t')
# db = pd.read_csv("example.tsv", delimiter='\t', index_col='user_id')
db = db[db['is_video'] == 1]

# print(db)

local_path = db['local_path'].tolist()
file_name = db['file_name'].tolist()
md5_hash = []
copy = []
reject = []

for i in range(db.shape[0]):
    full_name = os.path.join(local_path[i], file_name[i])
    if os.path.exists(full_name):
        md5_hash.append(md5(full_name))
    else:
        md5_hash.append("This file does not exist in this way!")

db['md5_hash'] = md5_hash
db = db.sort_values('md5_hash')

#print(db)

md5_hash = db['md5_hash'].tolist()
task_id = db['task_id'].tolist()

for item in md5_hash:
    if item != "This file does not exist in this way!":
        if md5_hash.count(item) > 1:
            copy.append(1)
        else:
            copy.append(0)
    else:
        copy.append("error")

#print(md5_hash)

for i in range(len(md5_hash)):
    if (i != 1) and (md5_hash[i] == md5_hash[i-1]):
        reject.append(1)
        json_check = {
            "status": "REJECTED",
            "public_comment": "Данное видео загружено повторно! Это нарушает правила выполнения задания!",
        }
        requests.patch(settings.URL_API + "assignments/%s" % task_id[i], headers=HEADERS, json=json_check)
        continue
    reject.append(0)

db['is_copy'] = copy
db['rejected'] = reject

pd.DataFrame(db).to_csv(f"pool_{settings.pool_id}_v2.tsv", index=False, sep="\t", encoding='utf-8')
# pd.DataFrame(db).to_csv("example_v2.tsv", index=False, sep="\t", encoding='utf-8')
