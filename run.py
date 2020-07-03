from src.ArchiveUtility import ArchiveUtility
from src.Downloader import Downloader
from src.FileOrganizer import FileOrganizer
from src.Utils import Utils


def handle_archival():
    print("Would you like to use an existing CSV file in the archival of files?")
    with_csv = Utils.get_string_input("Yes or no: ", ["YES", "NO"])

    directory, csv_path, column_number, destination_number, force, asset_prefix, source_name, directory_prefix = [
                                                                                                                     None] * 8

    if with_csv.upper() == "YES":
        csv_path = Utils.get_string_input("Enter the path to your CSV (i.e 'yourdirectory/yourcsv.csv'): ")
        column_number = Utils.get_string_input("Enter the column number for the file name's original name: ")
        destination_number = Utils.get_string_input("Enter the column number for the file name's expected new name: ")
        force = Utils.get_number_input(2,
                                       "Would you like to change the existing files' names or copy them into a new zipped "
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

    directory = Utils.get_string_input(
        "Enter the path to the directory containing all of the files you want to alter: ")

    input("Hit enter when you are ready to run.")

    ArchiveUtility(directory, asset_prefix, source_name, directory_prefix, csv_path, column_number,
                   destination_number, force).run()


def handle_file_organizer():
    organization_types = ["Dimension"]
    print("How would you like to organize your files?")
    for i, o_type in enumerate(organization_types):
        print(str(i + 1) + ":" + o_type)
    num = Utils.get_number_input(len(organization_types), "Enter Number: ")
    selected_type = organization_types[num - 1]

    src = Utils.get_string_input("Enter the source directory for all of your files you want to organize: ")
    dest = Utils.get_string_input("Enter the destination directory for all of the files you want to organize: ")

    run_forever = Utils.get_string_input("Would you like to run this continuously? (Yes or no): ", ["YES", "NO"])
    if run_forever.upper() == "YES":
        run_forever = True
    else:
        run_forever = False

    input("Hit enter when you are ready to run.")

    FileOrganizer(src, dest, selected_type).organize(run_forever)


def handle_dropbox_download():
    directory = input("Enter the directory path for your files (i.e /SS 01 FAMILY/TESTIMONIALS/200702): ")
    destination = input("Enter the path to the folder that you want the downloaded files in: ")
    api_key = input("Enter the API Key needed to access this account: ")

    input("Hit enter when you are ready to run.")
    Downloader(directory, destination, api_key).run()


def run():
    modes = {"Archival": handle_archival, "File Organize": handle_file_organizer, "Download": handle_dropbox_download}

    print("Welcome to the Media Utility Tool")
    print("What would you like to do?")
    for i, mode in enumerate(modes.keys()):
        print(str(i + 1) + ":" + mode)
    choice = Utils.get_number_input(len(modes), "Enter number: ")
    print("You selected: " + str(choice))
    mode = modes[list(modes.keys())[choice - 1]]
    mode()


if __name__ == '__main__':
    run()
