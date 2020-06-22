from glob import glob
from shutil import copyfile, move
import shutil
import csv
import os
import time
import json
import cv2

file_del = "/"
if os.name == 'nt':
    file_del = "\\"


def create_dir(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)


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


def get_number_input(size, msg):
    try:
        input_num = int(input(msg))
        if not input_num or input_num > size:
            return get_number_input(size, msg)
        else:
            return input_num
    except ValueError:
        print("Invalid Number Try Again")
        return get_number_input(size, msg)


def get_string_input(msg, expected=None):
    input_val = input(msg)

    if expected:
        if not input_val or input_val.upper() not in expected:
            return get_string_input(expected, msg)
    else:
        if not input_val:
            return get_string_input(expected, msg)

    return input_val


class ArchiveUtility(object):
    OUTPUT_FILE = 'archive'

    def __init__(self, directory, ap, sn, dp, csv_path, oc, dc, force=False):
        try:
            if directory[0] != file_del:
                self.directory = file_del + directory
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
            run()

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
                create_dir(self.OUTPUT_FILE)
            path = os.getcwd() + self.directory + file_del + "**"
            files_to_change = list(filter(lambda x: not os.path.isdir(x), glob(path, recursive=True)))
            if not files_to_change:
                ArchiveUtility.rm_dir(self.OUTPUT_FILE)
                self.clean(csvfile, "No files to archive found in: " + self.directory)
            for index, f_name in enumerate(files_to_change):
                fsplit = f_name.split(file_del)
                old_name = fsplit[-1]
                split_name = os.path.splitext(old_name)
                old_name = split_name[0]
                extension = split_name[1]
                if old_name in name_map:
                    old_dirs_set = fsplit[self.get_depth_to_base(fsplit[1:]):-1]
                    old_dirs = file_del.join(old_dirs_set)
                    new_name = name_map[old_name]
                    new_location = self.OUTPUT_FILE + file_del + old_dirs + file_del + new_name
                    if self.force:
                        new_path = old_dirs + file_del + new_name + extension
                        move(f_name, new_path)
                    else:
                        if old_dirs not in self.created_dirs:
                            self.create_directories(old_dirs_set)
                        copyfile(f_name, new_location)
                    print_progress_bar(index + 1, len(files_to_change))
            if self.force:
                self.clean(csvfile, "Finished. Your files are archived")
            else:
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
            create_dir(self.OUTPUT_FILE)
            path = os.getcwd() + self.directory + file_del + "**"
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
                fsplit = f_name.split(file_del)
                old_name = fsplit[-1]
                old_dirs_set = fsplit[self.get_depth_to_base(fsplit[1:]):-1]
                old_dirs = file_del.join(old_dirs_set)
                new_name = self.rename_file(old_name)

                new_location = self.OUTPUT_FILE \
                               + file_del + (self.dp if self.dp else "") \
                               + old_dirs + file_del + new_name

                if old_dirs not in self.created_dirs:
                    self.create_directories(old_dirs_set)

                copyfile(f_name, new_location)
                old_path = file_del.join(fsplit[4:-1])
                csv_writer.writerow([old_name, new_name, old_path, new_location])
                self.asset_number += 1
                print_progress_bar(index + 1, len(files_to_change))
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
                      + file_del + (self.dp if self.dp else "") \
                      + acc
            create_dir(new_dir)
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
    def rm_dir(dir_name):
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)


class FileOrganizer(object):

    def __init__(self, source_directory, destination_directory, organization_type):
        self.src_dir = source_directory
        self.dest_dir = destination_directory
        self.org_type = organization_type.upper()

    def organize(self, run_forever):
        path = os.getcwd() + file_del + self.src_dir + file_del + "**"

        def execute():
            files = list(filter(lambda x: not os.path.isdir(x), glob(path, recursive=True)))
            if files:
                print("New Files Found")
                for index, file in enumerate(files):
                    print_progress_bar(index + 1, len(files), "Organizing Files")
                    fsplit = file.split(file_del)
                    old_name = fsplit[-1]
                    if self.org_type == "DIMENSION":
                        vid = cv2.VideoCapture(file)
                        height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
                        width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
                        if height > width:
                            create_dir(self.dest_dir + "/vertical/")
                            create_dir(self.dest_dir + "/vertical/conform/")
                            move(file, self.dest_dir + "/vertical/conform/" + old_name)
                        else:
                            create_dir(self.dest_dir + "/")
                            move(file, self.dest_dir + "/" + old_name)

        if run_forever:
            while run_forever:
                time.sleep(1)
                execute()
        else:
            execute()


def handle_archival():
    print("Would you like to use an existing CSV file in the archival of files?")
    with_csv = get_string_input("Yes or no: ", ["YES", "NO"])

    directory, csv_path, column_number, destination_number, force, asset_prefix, source_name, directory_prefix = [
                                                                                                                     None] * 8

    if with_csv.upper() == "YES":
        csv_path = get_string_input("Enter the path to your CSV (i.e 'yourdirectory/yourcsv.csv'): ")
        column_number = get_string_input("Enter the column number for the file name's original name: ")
        destination_number = get_string_input("Enter the column number for the file name's expected new name: ")
        force = get_number_input(2, "Would you like to change the existing files' names or copy them into a new zipped "
                                    "directory? "
                                    "\n1. Existing File Names\n2. Copy It\nEnter Number:")
        if force == 1:
            force = True
        else:
            force = False

    elif with_csv.upper() == "NO":
        asset_prefix = input("Enter the asset prefix to append to the each renamed file (press enter to have none): ")
        source_name = input("Enter the source name (press enter to have none):")
        directory_prefix = input("Enter the prefix for your altered directories (i.e __archive) (press enter to have "
                                 "none): ")

    directory = get_string_input("Enter the path to the directory containing all of the files you want to alter: ")

    input("Hit enter when you are ready to run.")

    ArchiveUtility(directory, asset_prefix, source_name, directory_prefix, csv_path, column_number,
                   destination_number, force).run()


def handle_file_organizer():
    organization_types = ["Dimension"]
    print("How would you like to organize your files?")
    for i, o_type in enumerate(organization_types):
        print(str(i + 1) + ":" + o_type)
    num = get_number_input(len(organization_types), "Enter Number: ")
    selected_type = organization_types[num - 1]

    src = get_string_input("Enter the source directory for all of your files you want to organize: ")
    dest = get_string_input("Enter the destination directory for all of the files you want to organize: ")

    run_forever = get_string_input("Would you like to run this continuously? (Yes or no): ", ["YES", "NO"])
    if run_forever.upper() == "YES":
        run_forever = True
    else:
        run_forever = False

    input("Hit enter when you are ready to run.")

    FileOrganizer(src, dest, selected_type).organize(run_forever)


def run():
    modes = {"Archival": handle_archival, "File Organize": handle_file_organizer}

    print("Welcome to the Media Utility Tool")
    print("What would you like to do?")
    for i, mode in enumerate(modes.keys()):
        print(str(i + 1) + ":" + mode)
    choice = get_number_input(len(modes), "Enter number: ")
    print("You selected: " + str(choice))
    mode = modes[list(modes.keys())[choice - 1]]
    mode()


if __name__ == '__main__':
    run()
