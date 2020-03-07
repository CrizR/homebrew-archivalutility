import glob
from shutil import copyfile
import argparse
import shutil
import csv
import os
import time


class ArchiveUtility(object):
    OUTPUT_FILE = 'archive'

    def __init__(self, path, ap, sn, dp, file_del):
        if path[0] != file_del:
            self.path = file_del + path
        else:
            self.path = path
        self.ap = ap
        self.sn = sn
        self.dp = dp
        self.asset_number = 1000
        self.file_del = file_del

    def rename_file(self, file_name):
        return "ARC" + "_" + (self.ap if self.ap else "") + str(self.asset_number) + "_" + self.sn \
               + "_" + file_name

    def run(self):
        now = str(round(time.time() * 1000))
        csvfile = open(self.OUTPUT_FILE + "-" + now + ".csv", "w+")
        try:
            ArchiveUtility.rm_dir(self.OUTPUT_FILE)
            ArchiveUtility.create_dir(self.OUTPUT_FILE)
            path = os.getcwd() + self.path + self.file_del + "**"
            files_to_change = list(filter(lambda x: not os.path.isdir(x), glob.glob(path,
                                                                                    recursive=True)))
            csv_writer = csv.writer(csvfile, delimiter=',', quotechar='|',
                                    quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(["Original Name", "Archive Name", "Original Directory", "Archive Directory"])
            if not files_to_change:
                self.clean(csvfile, "No files to archive found in: " + self.path)
            for index, f_name in enumerate(files_to_change):
                old_name = f_name.split(self.file_del)[-1]
                old_dir = f_name.split(self.file_del)[-2]
                new_name = self.rename_file(old_name)

                new_location = self.OUTPUT_FILE \
                               + self.file_del + (self.dp if self.dp else "") \
                               + old_dir + self.file_del + new_name

                new_dir = self.OUTPUT_FILE \
                          + self.file_del + (self.dp if self.dp else "") \
                          + old_dir
                ArchiveUtility.create_dir(new_dir)
                copyfile(f_name, new_location)
                old_path = self.file_del.join(f_name.split(self.file_del)[4:-1])
                csv_writer.writerow([old_name, new_name, old_path, new_location])
                self.asset_number += 1
                ArchiveUtility.print_progress_bar(index, len(files_to_change))
            self.clean(csvfile, "Finished. Your archived files can be found in "
                       + self.OUTPUT_FILE + "-" + now + "/ and your csv in "
                       + self.OUTPUT_FILE + "-" + now + ".csv")
        except Exception as e:
            self.clean(csvfile, "Error: " + str(e))

    def clean(self, file, msg):
        print(msg)
        ArchiveUtility.rm_dir(self.OUTPUT_FILE)
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
    def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
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
    parser.add_argument('-p', '--path', help='File directory containing all the files (can include '
                                             'subdirectories)', required=True)
    parser.add_argument('-ap', '--assetPrefix', help='Prefix to asset number', required=False)
    parser.add_argument('-sn', '--sourceName', help='Name of Source', required=True)
    parser.add_argument('-dp', '--directoryPrefix', help='Prefix for archived directories', required=False)
    args = parser.parse_args()

    ArchiveUtility(args.path, args.assetPrefix, args.sourceName, args.directoryPrefix, file_del).run()
