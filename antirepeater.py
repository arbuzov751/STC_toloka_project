import settings
import hashlib
import os
import pandas as pd
import numpy as np


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

for i in range(db.shape[0]):
    full_name = os.path.join(local_path[i], file_name[i])
    if os.path.exists(full_name):
        md5_hash.append(md5(full_name))
    else:
        md5_hash.append("This file does not exist in this way!")

db['md5_hash'] = md5_hash
db = db.sort_values('md5_hash')

print(db)

copy = []
md5_hash = db['md5_hash'].tolist()
for item in md5_hash:
    if item != "This file does not exist in this way!":
        if md5_hash.count(item) > 1:
            copy.append(1)
        else:
            copy.append(0)
    else:
        copy.append("error")

db['is_copy'] = copy
db = db.sort_values('is_copy')
pd.DataFrame(db).to_csv(f"pool_{settings.pool_id}_v2.tsv", index=False, sep="\t", encoding='utf-8')
# pd.DataFrame(db).to_csv("example_v2.tsv", index=False, sep="\t", encoding='utf-8')
