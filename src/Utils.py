import os
import shutil


class Utils(object):

    @staticmethod
    def create_dir(dir_name):
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

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

    @staticmethod
    def get_number_input(size, msg):
        try:
            input_num = int(input(msg))
            if not input_num or input_num > size:
                return Utils.get_number_input(size, msg)
            else:
                return input_num
        except ValueError:
            print("Invalid Number Try Again")
            return Utils.get_number_input(size, msg)

    @staticmethod
    def get_string_input(msg, expected=None):
        input_val = input(msg)

        if expected:
            if not input_val or input_val.upper() not in expected:
                return Utils.get_string_input(expected, msg)
        else:
            if not input_val:
                return Utils.get_string_input(expected, msg)

        return input_val


    @staticmethod
    def rm_dir(dir_name):
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
