import requests

# you need to modify this to your zenodo ID
# zenodo_id = 2648592 # old grl data
# zenodo_id = 4739876 # new files...which
zenodo_id = 6799335
r = requests.get("https://zenodo.org/api/records/%i" % zenodo_id)

# sandbox version
# zenodo_id = 952702
# zenodo_id = 1035282 #second revision edition

# r = requests.get("https://sandbox.zenodo.org/api/records/%i" % zenodo_id)

file = open("zenodo_filelist.txt", "w")

for f in r.json()["files"]:
    file.write(f["links"]["self"] + "\n")

file.close()
