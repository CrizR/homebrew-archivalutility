import os
import time
from glob import glob
from shutil import move

from cv2 import cv2

from src.Utils import Utils

FILE_DEL = "/"
if os.name == 'nt':
    FILE_DEL = "\\"


class FileOrganizer(object):

    def __init__(self, source_directory, destination_directory, organization_type):
        self.src_dir = source_directory
        self.dest_dir = destination_directory
        self.org_type = organization_type.upper()

    def organize(self, run_forever):
        path = os.getcwd() + FILE_DEL + self.src_dir + FILE_DEL + "**"

        def execute():
            files = list(filter(lambda x: not os.path.isdir(x), glob(path, recursive=True)))
            if files:
                print("New Files Found")
                for index, file in enumerate(files):
                    Utils.print_progress_bar(index + 1, len(files), "Organizing Files")
                    fsplit = file.split(FILE_DEL)
                    old_name = fsplit[-1]
                    if self.org_type == "DIMENSION":
                        vid = cv2.VideoCapture(file)
                        height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
                        width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
                        if height > width:
                            Utils.create_dir(self.dest_dir + "/vertical/")
                            Utils.create_dir(self.dest_dir + "/vertical/conform/")
                            move(file, self.dest_dir + "/vertical/conform/" + old_name)
                        else:
                            Utils.create_dir(self.dest_dir + "/")
                            move(file, self.dest_dir + "/" + old_name)

        if run_forever:
            while run_forever:
                time.sleep(1)
                execute()
        else:
            execute()
