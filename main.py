import os
import shutil
import subprocess
from os.path import exists
import psutil
import time
import sys

blacklist = []
pid_blacklist = []
whitelist = []
pid_whitelist = []


def show_help():
    print("This application works by scanning for activity on SMTP ports 587 and 465 to find any communication being "
          "attempted over the network without your consent\n"
          "Available arguments:\n"
          "-s Performs a scan\n"
          "-a Adds program to startup directory\n"
          "-r Remove program from startup\n"
          "-w Displays contents of whitelist\n"
          "-b Displays contents of blacklist\n"
          "-x Exits the program.")


def scan():
    time = 1
    scans = 0
    # limits the number of times scans are run, so it is not indefinite
    while True:
        while scans < 3:
            if time == 1:
                print("\nScanning in progress...")
            # main command looks for activity on SMTP ports 587 (Gmail, Microsoft,AOL) and 465 (Yahoo and Live)
            proc = subprocess.Popen('netstat -ano -p tcp | findStr "587 465"', shell=True,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE)
            # popen.communicate() used internally for handling a timeout, specified in seconds
            out, err = proc.communicate()
            output = out.decode()
            grouped_output = output.split(" ")
            # Process ID (PID) will be the last number once split
            pid = grouped_output[-1]
            # output obtained from checking the application name associated with this PID
            command = subprocess.getoutput(f'tasklist /fi "pid eq {pid}"')
            # to make finding process name easier, split command
            process_name = command.split()

            time+=1
            # if SMTP communication is established
            if "ESTABLISHED" in output:
                # remove empty elements from the array
                grouped_output = list(filter(None, grouped_output))
                # get the full IP address with port number from the last element from output
                port_num = grouped_output[-3]
                # split at the ':' to get port number at last index of array
                get_port = port_num.split(":")
                port = get_port[-1]

                # get application name from the 13th element in process_name
                process_name = process_name[13]
                p = psutil.Process(int(pid))

                # check to see if the process is in the whitelist
                if process_name not in whitelist or pid not in pid_whitelist:
                    print("KEYLOGGER DETECTED!")
                    # if it isn't potential keylogger detected so check to see if it's in blacklist
                    # terminate application if it is in blacklist
                    if process_name in blacklist or pid in pid_blacklist:
                        p.kill()
                        print("Blacklist application found running.\nProcess automatically terminated.")
                        time=1
                        scans+=1
                    # if not in either list, check to see if it should be in whitelist
                    elif process_name not in whitelist or pid not in pid_whitelist:
                        print("Pausing application...\n")
                        # suspend application while user decides if it is dangerous or not
                        p.suspend()
                        print("Application Has Been Flagged as Potentially Harmful...\n")
                        print(f'Application name: {process_name}\n'
                              f'Process ID (PID): {pid}'
                              f'Trying to communicate on port {port}\n')
                        choice = False
                        while not choice:
                            # ask user if the process is benign and thus would be added to whitelist
                            is_safe = input("Would you like to whitelist this application? (Y/N): ").lower()
                            # if the user deems it as dangerous, terminate it and add to blacklist
                            if is_safe == 'n':
                                print("Terminating process...")
                                p.kill()
                                print("Adding to blacklist...")
                                blacklist.append(process_name)
                                pid_blacklist.append(pid)
                                choice = True
                                time=1
                                scans+=1
                            # if user says it is safe, resume and add to whitelist
                            elif is_safe == 'y':
                                print("Resuming process...")
                                p.resume()
                                print("Adding to whitelist...")
                                whitelist.append(process_name)
                                pid_whitelist.append(pid)
                                choice = True
                                time=1
                                scans+=1

                            print("Application whitelist:", whitelist)
                            print("Application blacklist:", blacklist)
                            print("PID whitelist: ", pid_whitelist)
                            print("PID blacklist: ", pid_blacklist)


def add_start():
    # checks to see if the program already exists in startup
    file_exists = exists("C:\\ProgramData\\Microsoft\\Windows\\Start "
                         "Menu\\Programs\\StartUp\\main.exe")
    # if it doesn't, add it
    if not file_exists:
        # get current path of file
        source = f'{os.getcwd()}\\main.exe'
        destination = ("C:\\ProgramData\\Microsoft\\Windows\\Start "
                       "Menu\\Programs\\StartUp\\main.exe")
        # copy source to destination
        shutil.copy(source, destination)
        # ensure the program has been copied successfully to startup
        file_exists = exists("C:\\ProgramData\\Microsoft\\Windows\\Start "
                             "Menu\\Programs\\StartUp\\main.exe")
        if file_exists:
            print("Program successfully added to startup.")
        else:
            print("Error: Program did not load into startup folder.")
    else:
        print("Error: Program already exists in startup.")


def remove_start():
    # check to see if the program is in the startup
    file_exists = exists("C:\\ProgramData\\Microsoft\\Windows\\Start "
                         "Menu\\Programs\\StartUp\\main.exe")
    # remove it if it is there
    if file_exists:
        os.remove("C:\\ProgramData\\Microsoft\\Windows\\Start "
                  "Menu\\Programs\\StartUp\\main.exe")
        # check to see if it has been removed successfully
        file_exists = exists("C:\\ProgramData\\Microsoft\\Windows\\Start "
                             "Menu\\Programs\\StartUp\\main.exe")
        if not file_exists:
            print("File removed successfully.")
        else:
            print("Error: File was not removed from startup.")
    else:
        print("Error: Program does not exist in startup directory.")


def show_whitelist():
    print(whitelist)
    time.sleep(4)


def show_blacklist():
    print(blacklist)
    time.sleep(4)


def main():
    selection = input("Option: ").lower()
    if selection == 'h':
        show_help()
        main()
    elif selection == 's':
        scan()
        main()
    elif selection == 'a':
        add_start()
        main()
    elif selection == 'r':
        remove_start()
        main()
    elif selection == 'w':
        show_whitelist()
        main()
    elif selection == 'b':
        show_blacklist()
        main()
    elif selection == 'x':
        sys.exit()

main()