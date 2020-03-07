import glob
from shutil import copyfile
import argparse
import shutil
import csv
import os
import time


class ArchiveUtility(object):
    OUTPUT_FILE = 'archive'

    def __init__(self, path, ap, sn, file_del):
        self.path = path
        self.ap = ap
        self.sn = sn
        self.asset_number = 1000
        self.csvfile = open(self.OUTPUT_FILE + ".csv", "w+")
        self.file_del = file_del

    def rename_file(self, file_name):
        return "ARC" + "_" + (self.ap if self.ap else "") + str(self.asset_number) + "_" + self.sn \
               + "_" + file_name

    def run(self):
        try:
            ArchiveUtility.rm_dir(self.OUTPUT_FILE)
            ArchiveUtility.create_dir(self.OUTPUT_FILE)
            path = os.getcwd() + self.path + self.file_del + "**"
            files_to_change = list(filter(lambda x: not os.path.isdir(x), glob.glob(path,
                                                                                    recursive=True)))
            csv_writer = csv.writer(self.csvfile, delimiter=',', quotechar='|',
                                    quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(["Original Name", "Archive Name", "Original Directory", "Archive Directory"])
            if not files_to_change:
                self.clean("No files to archive found in: " + self.path)
            for f_name in files_to_change:
                old_name = f_name.split(self.file_del)[-1]
                old_dir = f_name.split(self.file_del)[-2]
                new_name = self.rename_file(old_name)
                new_location = self.OUTPUT_FILE + self.file_del + old_dir + self.file_del + new_name
                new_dir = self.OUTPUT_FILE + self.file_del + old_dir
                ArchiveUtility.create_dir(new_dir)
                copyfile(f_name, new_location)
                old_path = self.file_del.join(f_name.split(self.file_del)[4:-1])
                csv_writer.writerow([old_name, new_name, old_path, new_location])
                self.asset_number += 1
            shutil.make_archive(self.OUTPUT_FILE + "-" + str(time.time()), 'zip', self.OUTPUT_FILE)
            self.clean("Finished. Your archived files can be found in " + self.OUTPUT_FILE + ".zip")
        except Exception as e:
            self.clean("Error: " + str(e))

    def clean(self, msg):
        print(msg)
        ArchiveUtility.rm_dir(self.OUTPUT_FILE)
        self.csvfile.close()
        exit(0)

    @staticmethod
    def create_dir(dir_name):
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

    @staticmethod
    def rm_dir(dir_name):
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)


if __name__ == '__main__':
    file_del = "/"
    if os.name == 'nt':
        file_del = "\\"
    parser = argparse.ArgumentParser(description='Archive Utility')
    parser.add_argument('-p', '--path', help='File directory containing all the files (can include '
                                             'subdirectories)', required=True)
    parser.add_argument('-ap', '--assetPrefix', help='Prefix to asset number', required=False)
    parser.add_argument('-sn', '--sourceName', help='Name of Source', required=True)
    args = parser.parse_args()

    ArchiveUtility(args.path, args.assetPrefix, args.sourceName, file_del).run()
