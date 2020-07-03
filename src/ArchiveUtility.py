import csv
import json
import os
import time
from glob import glob
from shutil import move, copyfile

from src.Utils import Utils

FILE_DEL = "/"
if os.name == 'nt':
    FILE_DEL = "\\"


class ArchiveUtility(object):
    OUTPUT_FILE = 'archive'

    def __init__(self, directory, ap, sn, dp, csv_path, oc, dc, force=False):
        try:
            if directory[0] != FILE_DEL:
                self.directory = FILE_DEL + directory
            else:
                self.directory = directory
            self.ap = ap
            self.sn = sn
            self.dp = dp
            self.asset_number = 1000
            if csv_path:
                self.with_csv = True
            else:
                self.with_csv = False
            self.csv_path = csv_path
            self.oc = int(oc)
            self.dc = int(dc)
            self.force = force
            self.created_dirs = {}
        except:
            print("\n\nInvalid Input\n\n")

    def rename_file(self, file_name):
        return "ARC" + "_" + (self.ap if self.ap else "") + str(self.asset_number) + "_" + self.sn \
               + "_" + file_name

    def run(self):
        if self.with_csv:
            self._run_with_csv()
        else:
            self._run_default()

    def _run_with_csv(self):
        now = str(round(time.time() * 1000))
        self.OUTPUT_FILE += "-" + now
        csvfile = open(self.csv_path, "r")
        csvfile.read(1)
        name_map = {}
        for line in csvfile.readlines():
            line = line.split(",")
            original_name = line[self.oc]
            new_name = line[self.dc]
            name_map[original_name] = new_name

        with open('test.json', "w+") as file:
            file.writelines(json.dumps(name_map))
        try:
            ArchiveUtility.rm_dir(self.OUTPUT_FILE)
            if not self.force:
                Utils.create_dir(self.OUTPUT_FILE)
            path = os.getcwd() + self.directory + FILE_DEL + "**"
            files_to_change = list(filter(lambda x: not os.path.isdir(x), glob(path, recursive=True)))
            if not files_to_change:
                ArchiveUtility.rm_dir(self.OUTPUT_FILE)
                self.clean(csvfile, "No files to archive found in: " + self.directory)
            for index, f_name in enumerate(files_to_change):
                fsplit = f_name.split(FILE_DEL)
                old_name = fsplit[-1]
                split_name = os.path.splitext(old_name)
                old_name = split_name[0]
                extension = split_name[1]
                if old_name in name_map:
                    old_dirs_set = fsplit[self.get_depth_to_base(fsplit[1:]):-1]
                    old_dirs = FILE_DEL.join(old_dirs_set)
                    new_name = name_map[old_name]
                    new_location = self.OUTPUT_FILE + FILE_DEL + old_dirs + FILE_DEL + new_name
                    if self.force:
                        new_path = old_dirs + FILE_DEL + new_name + extension
                        move(f_name, new_path)
                    else:
                        if old_dirs not in self.created_dirs:
                            self.create_directories(old_dirs_set)
                        copyfile(f_name, new_location)
                    Utils.print_progress_bar(index + 1, len(files_to_change))
            if self.force:
                self.clean(csvfile, "Finished. Your files are archived")
            else:
                self.clean(csvfile, "Finished. Your archived files can be found in "
                           + self.OUTPUT_FILE + "-" + now + "|| 00111100 00110011")
        except Exception as e:
            Utils.rm_dir(self.OUTPUT_FILE)
            self.clean(csvfile, "Error: " + str(e))

    def _run_default(self):
        now = str(round(time.time() * 1000))
        self.OUTPUT_FILE += "-" + now
        csv_filename = self.OUTPUT_FILE + "-" + now + ".csv"
        csvfile = open(csv_filename, "w+")
        try:
            Utils.rm_dir(self.OUTPUT_FILE)
            Utils.create_dir(self.OUTPUT_FILE)
            path = os.getcwd() + self.directory + FILE_DEL + "**"
            files_to_change = list(filter(lambda x: not os.path.isdir(x), glob(path,
                                                                               recursive=True)))
            csv_writer = csv.writer(csvfile, delimiter=',', quotechar='|',
                                    quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(["Original Name", "Archive Name", "Original Directory", "Archive Directory"])
            if not files_to_change:
                os.remove(csv_filename)
                ArchiveUtility.rm_dir(self.OUTPUT_FILE)
                self.clean(csvfile, "No files to archive found in: " + self.directory)
            for index, f_name in enumerate(files_to_change):
                fsplit = f_name.split(FILE_DEL)
                old_name = fsplit[-1]
                old_dirs_set = fsplit[self.get_depth_to_base(fsplit[1:]):-1]
                old_dirs = FILE_DEL.join(old_dirs_set)
                new_name = self.rename_file(old_name)

                new_location = self.OUTPUT_FILE \
                               + FILE_DEL + (self.dp if self.dp else "") \
                               + old_dirs + FILE_DEL + new_name

                if old_dirs not in self.created_dirs:
                    self.create_directories(old_dirs_set)

                copyfile(f_name, new_location)
                old_path = FILE_DEL.join(fsplit[4:-1])
                csv_writer.writerow([old_name, new_name, old_path, new_location])
                self.asset_number += 1
                Utils.print_progress_bar(index + 1, len(files_to_change))
            self.clean(csvfile, "Finished. Your archived files can be found in "
                       + self.OUTPUT_FILE + "-" + now + "/ and your csv in "
                       + csv_filename + " || 00111100 00110011")
        except Exception as e:
            os.remove(csv_filename)
            Utils.rm_dir(self.OUTPUT_FILE)
            self.clean(csvfile, "Error: " + str(e))

    def create_directories(self, dir_set):
        acc = ""
        for dir in dir_set:
            acc += dir + FILE_DEL
            new_dir = self.OUTPUT_FILE \
                      + FILE_DEL + (self.dp if self.dp else "") \
                      + acc
            Utils.create_dir(new_dir)
        self.created_dirs[acc] = True

    def get_depth_to_base(self, fsplit):
        depth = 0
        for element in fsplit:
            if element in self.directory:
                return depth + 1
            depth += 1

    def clean(self, file, msg):
        print(msg)
        file.close()
        exit(0)
