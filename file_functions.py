#Version 0.1
### Por https://github.com/Enzostik.

import os
import sys

#Para manejar archivos y directorios
def get_dirname(__file__:str)->str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

def check_dir(path:str)->str:
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def get_files_from_folder(path:str)->list:
    if not os.path.exists(path): return []
    return

def change_ext(path:str, now_:str, new_:str):
    if not os.path.exists(path):
        print("ERROR: Folder not found")
        return
    for file in os.listdir(path):
        infile = os.path.join(path, file)
        if not os.path.isfile(infile):  continue
        newfile = infile.replace(now_, new_)
        os.rename(infile,newfile)
