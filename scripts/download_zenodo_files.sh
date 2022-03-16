#!/bin/bash

# Create filelist !!!YOU HAVE TO CHANGE YOUR Repository ID
python scripts/parse_filenames.py

cd data

# # remove possible old file
# rm -f busecke_etal_2021_aguadv.tar*

#download the files in the list
wget -i ../zenodo_filelist.txt

#delete the filelist
rm ../zenodo_filelist.txt

#unzip
tar -xf busecke_etal_2021_aguadv.tar
