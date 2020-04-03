from glob import glob
from shutil import copyfile
import argparse
import shutil
import csv
import os
import time
import json


class ArchiveUtility(object):
    OUTPUT_FILE = 'archive'

    def __init__(self, directory, ap, sn, dp, file_del, csv_path, oc, dc):
        if directory[0] != file_del:
            self.directory = file_del + directory
        else:
            self.directory = directory
        self.ap = ap
        self.sn = sn
        self.dp = dp
        self.asset_number = 1000
        self.file_del = file_del
        if csv_path:
            self.with_csv = True
        else:
            self.with_csv = False
        self.csv_path = csv_path
        self.oc = int(oc)
        self.dc = int(dc)
        self.created_dirs = {}

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
            ArchiveUtility.create_dir(self.OUTPUT_FILE)
            path = os.getcwd() + self.directory + self.file_del + "**"
            files_to_change = list(filter(lambda x: not os.path.isdir(x), glob(path, recursive=True)))
            if not files_to_change:
                ArchiveUtility.rm_dir(self.OUTPUT_FILE)
                self.clean(csvfile, "No files to archive found in: " + self.directory)
            for index, f_name in enumerate(files_to_change):
                fsplit = f_name.split(self.file_del)
                old_name = fsplit[-1]
                if old_name in name_map:
                    old_dirs_set = fsplit[self.get_depth_to_base(fsplit[1:]):-1]
                    old_dirs = self.file_del.join(old_dirs_set)
                    if "." in old_name:
                        old_name = old_name.split(".")[0]
                    new_name = name_map[old_name]
                    new_location = self.OUTPUT_FILE + self.file_del + old_dirs + self.file_del + new_name
                    if old_dirs not in self.created_dirs:
                        self.create_directories(old_dirs_set)
                    copyfile(f_name, new_location)
                    print("TEST")
                    self.asset_number += 1
                    ArchiveUtility.print_progress_bar(index + 1, len(files_to_change))
            self.clean(csvfile, "Finished. Your archived files can be found in "
                       + self.OUTPUT_FILE + "-" + now + "|| 00111100 00110011")
        except Exception as e:
            ArchiveUtility.rm_dir(self.OUTPUT_FILE)
            self.clean(csvfile, "Error: " + str(e))

    def _run_default(self):
        now = str(round(time.time() * 1000))
        self.OUTPUT_FILE += "-" + now
        csv_filename = self.OUTPUT_FILE + "-" + now + ".csv"
        csvfile = open(csv_filename, "w+")
        try:
            ArchiveUtility.rm_dir(self.OUTPUT_FILE)
            ArchiveUtility.create_dir(self.OUTPUT_FILE)
            path = os.getcwd() + self.directory + self.file_del + "**"
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
                fsplit = f_name.split(self.file_del)
                old_name = fsplit[-1]
                old_dirs_set = fsplit[self.get_depth_to_base(fsplit[1:]):-1]
                old_dirs = self.file_del.join(old_dirs_set)
                new_name = self.rename_file(old_name)

                new_location = self.OUTPUT_FILE \
                               + self.file_del + (self.dp if self.dp else "") \
                               + old_dirs + self.file_del + new_name

                if old_dirs not in self.created_dirs:
                    self.create_directories(old_dirs_set)

                copyfile(f_name, new_location)
                old_path = self.file_del.join(fsplit[4:-1])
                csv_writer.writerow([old_name, new_name, old_path, new_location])
                self.asset_number += 1
                ArchiveUtility.print_progress_bar(index + 1, len(files_to_change))
            self.clean(csvfile, "Finished. Your archived files can be found in "
                       + self.OUTPUT_FILE + "-" + now + "/ and your csv in "
                       + csv_filename + " || 00111100 00110011")
        except Exception as e:
            os.remove(csv_filename)
            ArchiveUtility.rm_dir(self.OUTPUT_FILE)
            self.clean(csvfile, "Error: " + str(e))

    def create_directories(self, dir_set):
        acc = ""
        for dir in dir_set:
            acc += dir + file_del
            new_dir = self.OUTPUT_FILE \
                      + self.file_del + (self.dp if self.dp else "") \
                      + acc
            ArchiveUtility.create_dir(new_dir)
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

    @staticmethod
    def create_dir(dir_name):
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

    @staticmethod
    def rm_dir(dir_name):
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

    @staticmethod
    def print_progress_bar(iteration, total, prefix='Archiving Files', suffix='', decimals=2, length=100, fill='█',
                           print_end="\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=print_end)
        # Print New Line on Complete
        if iteration == total:
            print()


if __name__ == '__main__':
    file_del = "/"
    if os.name == 'nt':
        file_del = "\\"
    parser = argparse.ArgumentParser(description='Archive Utility')
    parser.add_argument('-dir', '--directory',
                        help='File directory containing all the files (can include subdirectories)', required=True)

    # Without CSV
    parser.add_argument('-ap', '--assetPrefix', help='Prefix to asset number', required=False)
    parser.add_argument('-sn', '--sourceName', help='Name of Source', required=False)
    parser.add_argument('-dp', '--directoryPrefix', help='Prefix for archived directories', required=False)

    # With CSV
    parser.add_argument('-cp', '--csvPath', help='The file path of the csv to use', default=None, required=False)
    parser.add_argument('-oc', '--originalColumn', help='The column number to use as the file name key',
                        default=None,
                        required=False)
    parser.add_argument('-dc', '--destinationColumn', help='The column number to use as the file names new value',
                        default=None,
                        required=False)

    args = parser.parse_args()

    ArchiveUtility(args.directory, args.assetPrefix, args.sourceName, args.directoryPrefix, file_del,
                   args.csvPath, args.originalColumn, args.destinationColumn).run()
