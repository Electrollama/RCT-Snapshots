from matplotlib import pyplot as plt
from PIL import Image
from file_tools import *
from numpy import array
from os.path import basename
from tkinter import Tk, filedialog
from os import listdir, path, mkdir

def file_dialog(folder=False, types=(('CSV', '.csv'),)):
    root = Tk()
    if folder:
        folder_path = filedialog.askdirectory(parent=root)
        root.destroy()
        files = listdir(folder_path)
        files = [folder_path + '/' + f for f in files]
        folder_name = basename(folder_path)
        print("Opened {} files from {}".format(len(files), folder_name))
        print("   path: {}".format(folder_path))
        return files, folder_name
    else:
        file_path = filedialog.askopenfilename(filetypes=types)
        root.destroy()
        print("Opened: {}".format(file_path))
        return file_path

file_paths, folder_path = file_dialog(True)
for im_path in file_paths:
    im = Image.open(im_path)
    cropped = im.crop([0, 30, 1000, 732])
    im.convert('RGB').save(im_path[:-4]+'.jpg', 'JPEG')