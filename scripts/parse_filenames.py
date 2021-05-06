import requests

# you need to modify this to your zenodo ID
zenodo_id = 2648592 # old grl data
# zenodo_id = 4739876 # new files...which dont work yet...

# r = requests.get("https://zenodo.org/api/records/%i" % zenodo_id)

# sandbox version
zenodo_id = 812722
r = requests.get("https://sandbox.zenodo.org/api/records/%i" % zenodo_id)

file = open("zenodo_filelist.txt", "w")

for f in r.json()["files"]:
    file.write(f["links"]["self"] + "\n")

file.close()
