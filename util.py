# import requests
import string
import random


class Utilities:

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    EXCEPTION = '\033[96m'

    def printSuccess(msg):
        print(Utilities.OKGREEN + "[OK]" + msg + Utilities.ENDC)

    def printError(msg):
        print(Utilities.FAIL + "[ERROR]" + msg + Utilities.ENDC)

    def printException(msg):
        print(Utilities.FAIL + "[EXCEPTION]" + msg + Utilities.ENDC)
    
    def printLog(msg):
        print(Utilities.OKBLUE + "[LOG]" + msg + Utilities.ENDC)

    def gen_code(size = 16, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
        return ''.join(random.SystemRandom().choice(chars) for _ in range(size))
    
    def write_to_file(msg):
        print("Summary:")
        print("--------")
        print(msg)
        print("--------")
        print("Summary also written to file \'User_details_toMail.txt\'")
        f = open('User_details_toMail.txt', 'w')
        f.write(msg)