#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse

OK = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

def run_test(dirs, args):

    total = 0
    success = 0
    sanity_error = 0

    for dir in dirs:

        total_cat = 0
        success_cat = 0
        print(BOLD + dir + END, end='\n\n')
        try:
            for f in os.listdir(dir):
                with open(dir + '/' + f, 'r') as file:
                    data = file.readlines()
                    binaries = data[0].split(",")
                    my_binary = binaries[1].replace('\n', "").split(' ')
                    binary = binaries[0].split(' ')
                test = data[1].replace('\n', "")
                if args.sanity:
                    sanity_error = sanity_test(test, my_binary, args)
                    if sanity_error:
                        total_cat += 1
                        continue
                success_cat += make_test(test, my_binary, binary, args)
                total_cat += 1
        except FileNotFoundError:
            print("No available test for " + dir)
            return
        print_result(total_cat, success_cat, args)
        total += total_cat
        success += success_cat

    print(UNDERLINE + "%d%%" % (success / total * 100) + END + " of test succeeded for a total of " + UNDERLINE + "%d" % total + END + " tests.")


def sanity_test(arg, my_binary, argv):

    args = [arg]
    try:
        sanity_result = subprocess.run(['valgrind'] + my_binary + args,
                    stderr=subprocess.PIPE, stdout=subprocess.PIPE, timeout=argv.timeout)
    except subprocess.TimeoutExpired:
        print(FAIL + "TIMEOUT " + END + ' ' * 34 + '-- for ' + ' '.join(args))
        return 1

    summary = sanity_result.stderr.decode("utf-8")
    if "0 errors" in summary and ("definitely lost: 0 bytes" \
        in summary or not "definitely lost" in summary):
        return 0
    elif not argv.quiet:
        print(FAIL + "MEMORY ERROR DETECTED " + END + ' ' * 20 + '-- for ' + ' '.join(args))
        return 1


def print_result(total, success, argv):

    if not argv.quiet:
        print()
    print('[', OK + 'OK' if success is total
            else WARNING + 'WARNING' if success is not 0
            else FAIL + 'FAIL', end='')
    print(END + ' ]', end = ' ')
    print("Success %d/%d" % (success, total), end='\n\n')


def make_test(arg, my_binary, binary, argv):

    args = [arg]
    try:
        myresult = subprocess.run(my_binary + args,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=argv.timeout)
    except subprocess.TimeoutExpired:
        print(FAIL + "TIMEOUT " + END + ' ' * 34 + "-- for " + ' '.join(args))
        return 0

    goodresult = subprocess.run(binary + args,
               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fail = 0
    space_nb = 42

    if myresult.stdout != goodresult.stdout:
        fail += 1
        if not argv.quiet:
            print(FAIL + "stdout " + END + "wrong ", end='')
        space_nb -= 13
    if not myresult.stderr.decode("utf-8") and  goodresult.stderr.decode("utf-8") \
       or myresult.stderr.decode("utf-8") and not goodresult.stderr.decode("utf-8") : 
        fail += 1
        if not argv.quiet:
            print(FAIL + "stderr " + END + "wrong ", end='')
        space_nb -= 13
    if myresult.returncode != goodresult.returncode:
        fail += 1
        if not argv.quiet:
            print(FAIL + "exit code " + END + "wrong" + (' ' if fail  else ''), end='')
        space_nb -= 16
    elif not fail:
        if not argv.quiet:
            print(OK + 'SUCCESS' + END + ' ' * 35 + '-- for  ' + ' '.join(args))
        return 1
    if not argv.quiet:
        print(' ' * space_nb + '-- for ' + ' '.join(args))
    return 0


def get_categories():

    L = []
    for files in os.listdir("."):
        if os.path.isdir(files):
            L.append(files)
    return L


def parse_arg():

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", help="print category list", action="store_true")
    parser.add_argument("-c", "--category", help="only execute test of the specified category",
                        type=str)
    parser.add_argument("-t", "--timeout", help="set timout for command in seconds",
                        type=float)
    parser.add_argument("-s", "--sanity", help="run test with valgrind", action="store_true")
    parser.add_argument("-q", "--quiet", help="quiet mode", action="store_true")
    return parser.parse_args()


def print_categories(L):

    print("Available categories : ")
    for cat in L:
        print(BOLD + cat + END + ' | ', end='')


def main():
    
    args = parse_arg()
    L = get_categories()
    if args.list:
        print_categories(L)
        return
    if args.category:
        L = [args.category]
    run_test(L, args)

if __name__=='__main__':
    main()
