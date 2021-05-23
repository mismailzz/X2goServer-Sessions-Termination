#! /usr/bin/python3.6
import sys
import getopt
import os
import getpass
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from time import sleep

def help_function():
    print("")
    print("")
    print("----------------------------Help----------------------------")
    print("./x2gosession_status [OPTIONS]------")
    print("")
    print("-h               ,   For help")
    print("-l               ,   For login user")
    print("-password        ,   For login user password")
    print("-u               ,   For target user")
    print("-s               ,   For Server IP list file")
    print("-k               ,   For Kill session [all] [sleep]")
    print("-o               ,   For Session status [all]")
    print("")
    print("")

def execute_command_getstatus(target_user, login_user, password, server_option):
    client_xserver = "@" + server_option #SERVER IP FILE
    session_status_command = "bolt script run ./userX2goSessionStatus.sh " + target_user +" --no-host-key-check --tmpdir=/home/"+ login_user +" -p "+ password +" --tty --targets " + client_xserver +  " -u "+login_user+" 1>"+outputfile +" 2> " + errorfile
    #print(session_status_command)
    try:
        os.system(session_status_command) #EXECUTE THE COMMAND
    except Exception as e:
    #    print(e)
        sys.exit(2) #EXIT
    
def kill_user_session(target_user, killsession, server_option, outputkill, errorkill, login_user, password):
    
    execute_command_getstatus(target_user, login_user, password, server_option) #GET THE RECENT UPDATE OUTPUT FILE STATUS OF SESSIONS
    session_result = jsonFormatBoltOutput(server_option, outputfile) #GET THE GONVERTED DICTIONARY SESSIONS INFORMATION

    #print(session_result)
    #CLEANING THE DICT BY REMOVING UNWANTED VALUES
    session_result = { key : value for key, value in session_result.items() if "No Session Created Here" not in value}
    #print(session_result)

    #CREATING THE NEW DICTIONARY THAT WOULD CARRY THE FINAL DICT ON WHICH WE WILL PERFORM ACTION
    session_kill_dict = dict()
    for i in session_result.keys():
        session_kill_dict[i] = []

    red_flag = False #IF NO OPTION IS SELECT FOR KILLSESSION VARIABLE THEN EXIT
    
    #KILL ALL SESSIONS DICT
    if killsession == "sleep": #MAKE DICT FOR SLEEP SESSIONS FOR THE USER
        for key, values in session_result.items():
            #print(key)
            #print(len(values))
            #print(values)
            for value in values:
                #print(value)
                temp_session_split_info = value.split(',')
                #print(temp_session_split_info)
                if temp_session_split_info[2] == 'S':
                    session_kill_dict[key].append(value)
        session_result = session_kill_dict
        red_flag = True
    elif killsession == "all": #ALREADY THE DICT FOR ALL SESSIONS FOR THE USER
        print("")
        confirm = input("Are you sure to terminate all sessions[Y/N]: ") #FINAL CONFIRMATION FOR BIG STEP
        if confirm == 'y' or 'Y':
            red_flag = True
        elif confirm == 'n' or 'N':
            sys.exit(2)
        else:
            sys.exit(2)
    
    session_result = { key : value for key, value in session_result.items() if value} #REMOVAL SERVER FROM DICT OF THE EMPTY LIST SESSION 
    
    if red_flag == True:
        #print(session_result)
        return session_result
    else:
        print("")
        help_function()

def execute_command_killsession(status_list_dict, outputkill, errorkill, login_user, password):
    
    #LOADING BAR FOR STATUS
    console = Console()
    tasks = [f"Server {n}" for n in status_list_dict]
    with console.status("[bold green]Working on tasks...") as status:
    
        for server, session_list in status_list_dict.items():
            temp_serverPerSessionsTotal = ""
            for session in session_list:
                temp = session.split(',')
                session_id = temp[0]
                if temp_serverPerSessionsTotal == "":
                    temp_serverPerSessionsTotal = session_id
                else:
                    temp_serverPerSessionsTotal = temp_serverPerSessionsTotal + " " + session_id
            session_kill = "bolt script run ./kill_user_sessions.sh " + temp_serverPerSessionsTotal + " --no-host-key-check --tmpdir=/home/"+ login_user+" -p "+ password + " --tty --targets " + server +  " -u "+ login_user+" 1>"+outputkill +" 2> " + errorkill
            #print(session_kill)
            os.system(session_kill)
            
            #LOADING BAR FOR STATUS
            task = tasks.pop(0)
            console.log(f"{task} complete")
            #-----------------------


    print("")
    print("Session has been terminated")
    print('\033[31m' + ':) No way to back')
    print('\033[39m')
    print("")

def kill_all_sleep_session(serverlist_file, outputkill, errorkill, login_user, password):

    #client_xserver = "@" + server_option
    #session_kill = "bolt script run ./kill_all_sleep.sh --no-host-key-check --tmpdir=/home/"+ login_user+" -p "+ password + " --tty --targets " + client_xserver +  " -u "+ login_user +" 1>"+outputkill +" 2> " + errorkill
        
    ip_addresses_file = open(serverlist_file,"r")
    ip_addresses = ip_addresses_file.readlines()
    #print(ip_addresses)
    ip_field = []
    for line in ip_addresses:
        ip_field.append(line.strip())

    #LOADING BAR FOR STATUS
    console = Console()
    tasks = [f"Server {n}" for n in ip_field]
    with console.status("[bold green]Working on tasks...") as status:
        
        for server_ip in ip_field:
            session_kill = "bolt script run ./kill_all_sleep.sh --no-host-key-check --tmpdir=/home/"+ login_user+" -p "+ password + " --tty --targets " + str(server_ip) +  " -u "+ login_user +" 1>"+outputkill +" 2> " + errorkill
            os.system(session_kill)

            #LOADING BAR FOR STATUS
            task = tasks.pop(0)
            console.log(f"{task} complete")
            #-----------------------
    
    print("")
    print("All sleeping sessions have been terminated")
    print('\033[31m' + ':) For All Users From All Selected Servers')
    print('\033[39m')
    print("")

def all_session_status(server_option, login_user, password, outputfile, errorfile):

    client_xserver = "@" + server_option #SERVER IP FILE
    session_status_command = "bolt script run ./allUserSessionStatus.sh " + " --no-host-key-check --tmpdir=/home/"+ login_user +" -p "+ password +" --tty --targets " + client_xserver +  " -u "+login_user+" 1>"+outputfile +" 2> " + errorfile
    #print(session_status_command)
    try:
        os.system(session_status_command) #EXECUTE THE COMMAND
    except Exception as e:
        print(e)
        sys.exit(2) #EXIT

def jsonFormatBoltOutput(serverlist_file, outputfile):
    
    ip_addresses_file = open(serverlist_file,"r")
    ip_addresses = ip_addresses_file.readlines()
    #ip_addresses_list = ip_addresses.split("\n")
    #print(ip_addresses_list)
    # Using readlines()
    ip_field = []
    for line in ip_addresses:
        ip_field.append(line.strip())
    #print(ip_field)

    session_list = dict()
    for ip_key in ip_field:
        session_list[ip_key] = []
    #print(session_list)

    #READ PUPPET BOLT OUTPUT FILE  
    sessions_info_file = open(outputfile, "r")
    sessions_info = sessions_info_file.readlines()
    select_ip = ""
    ip_found = False
    for line in sessions_info:
        read_line = line.rstrip("\n")
        read_line = read_line.replace(':','')
        if "Finished" in read_line:
            temp = read_line.split(" ") #selecting the key value
            select_ip = temp[2]
            select_ip =  ' '.join(select_ip.split())
            #print(select_ip) 
            ip_found = True
        if ip_found == True and "STDOUT" not in read_line and "Successful" not in read_line and "Ran on" not in read_line and "Finished" not in read_line:
            if "No Session Created Here" not in read_line:
                
                # BELOW COMMENTED INFORMATION SEND ONLY ID INFO
                '''
                split_comma = read_line.split(",")
                session_id_info = split_comma[0]
                session_id_info = ' '.join(session_id_info.split())
                session_list[select_ip].append(session_id_info)
                '''
                #DUE TO THE NEED OF COMPELETE INFO WE HAVE TO SEND COMPLETE ID INFO WITH STATUS
                session_id_info = '\n'.join(read_line.split())
                session_list[select_ip].append(session_id_info)

                #print(session_list)
            else:
                #print("there")
                #print(read_line)
                read_line = ' '.join(read_line.split())
                session_list[select_ip].append(read_line)
                #print(session_list)

    #print(session_list)
    return session_list #PASSING THE DICTIONARY

def tableFormatOutput(serverlist_file, outputfile):
    
    session_result = jsonFormatBoltOutput(serverlist_file, outputfile)
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Server IPs", style="dim", width=12)
    table.add_column("Sessions")
    table.add_column("Run Session", justify="right")
    table.add_column("Sleep Sessions", justify="right")

    
    for key, values in session_result.items():
        sessions_status_list = ""
        sleep_session_count = 0
        run_session_count = 0
        #print(values)
        #LOOP TO COUNT THE SESSIONS STATUS
        for value in values:
            #print(value)
            try:
                if "No Session Created Here" not in value:
                    temp = value.split(',') 
                    if temp[2] == "S":
                        sleep_session_count = sleep_session_count + 1
                    elif temp[2] == "R":
                        run_session_count = run_session_count + 1

            except Exception as identifier:
                #print (identifier)
                pass
            '''
            if "No Session Created Here" not in value:
                temp = value.split(',') 
                if temp[2] == "S":
                   sleep_session_count = sleep_session_count + 1
                elif temp[2] == "R":
                    run_session_count = run_session_count + 1
                #print(temp)
            '''
        
        sessions_status_list = '\n' .join(values)
        table.add_row( key, sessions_status_list, str(run_session_count), str(sleep_session_count))
    
    console.print(table)

#===================================================================================================================================================================
###------------------------------------------------------------------------MAIN FUNCTION----------------------------------------------------------------------------

login_user = ""                                             #THE ADMIN LOGIN USERNAME
password = ""                                               #THE ADMIN LOGIN USER PASSWORD
server_option = ""                                          #LIST OF SERVERS ON WHICH ACTION TO BE TAKEN
target_user = ""                                            #TARGET USER ON WHICH ACTION TO BE TAKEN
outputfile = "output.txt"                                   #OUTPUT STORED IN IT FOR PUPPEPT BOLT SESSION STATUS TO WORKING AFTER PARSING AND ALSO TO TROUBLESHOOT
errorfile="error.txt"                                       #ERROR OUTPUT OF PUPPET BOLT 
outputkill = "outputkill.txt"                               #SIMILARLY INFORMATION OF BOLT OUTPUT AFTER KILLING SESSIONS
errorkill="errorkill.txt"                                   #SAME AS ABOVE
killsession = ""                                            #GET THE ADMIN CHOICE TO KILL SESSION SLEEP OR ALL
status_arg = ""                                             #GET THE STATUS OF THE ALL SESSIONS IRRESPECTIVE OF SPECIFIC USER

###----------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------TO GET COMMAND LINE ARGUMENTS------------------------------------------------------------------
try:
    #COMMAND LINE OPTIONS
    opts, args = getopt.getopt(sys.argv[1:], 'o:u:s:k:l:p:h', ['output=', 'user=', 'server=', 'kill=', 'loginuser=', 'password=','help'])
except getopt.GetoptError:
    #ERROR
    help_function()
    sys.exit(2)
#-------------------------------------------------------------------ASSINGMENTS FOR REQUIRED ACTIONS --------------------------------------------------------------
for opt, arg in opts:
    if opt in ('-h', '--help'):                             #HELP
        help_function()
        sys.exit(2)
    elif opt in ('-l', '--loginuser'):                      #LOGIN USER [ADMIN]
        login_user = arg
    elif opt in ('-p', '--password'):                       #LOGIN USER [ADMIN] PASSWORD
        try:
            password = getpass.getpass(prompt='Password? ')
        except Exception as e:
            print(e)
            sys.exit(2)
    elif opt in ('-u', '--user'):                           #TARGET USER NAME [TO ANALYZE THE SESSIONS]
        target_user = arg
    elif opt in ('-o', '--output'):                         #FOR ALL SLEEP/RUN SESSIONS  
        status_arg = arg
    elif opt in ('-s', '--server'):                         #RUNNING NODES [XSERVER] INFORMATION
        server_option = arg
        if os.path.exists(server_option) == False:
            print("")
            print(" <!> Xserver IP Address list file not found ")
            print("")
            sys.exit(2)
    elif opt in ('-k', '--session'):                        #FOR KILL SESSIONS [SLEEP OR ALL (RUN AND SLEEP)]
        killsession = arg
    else:
        help_function()
        sys.exit(2)
#-------------------------------------------------------------------ACTIONS TO BE TAKEN ON INPUT-------------------------------------------------------------------
#CONTROL THE MAIN FUNCTION
if (target_user != "" and server_option != "" and killsession == "" and login_user != "" and password != "" and server_option != ""): #GET THE STATUS OF THE USER
    
    execute_command_getstatus(target_user, login_user, password, server_option) #EXECUTE THE COMMAND
    tableFormatOutput(server_option, outputfile) #FORMAT OUTPUT TO TABLE AND PRINT ON SCREEN
    #[OK]

elif((killsession == "all" or killsession == "sleep") and (target_user != "" and server_option != "" and login_user != "" and password != "")):#KILL THE SLEEP OR ALL SESSIONS OF USER

    kill_sessions_info = kill_user_session(target_user, killsession, server_option, outputkill, errorkill, login_user, password)
    #print(kill_sessions_info)
    execute_command_killsession(kill_sessions_info, outputkill, errorkill, login_user, password)

    #TO PRINT THE OUTPUT STATUS FOR ALL SESSIONS RESPECTIVE OF USER
    execute_command_getstatus(target_user, login_user, password, server_option) #EXECUTE THE COMMAND
    tableFormatOutput(server_option, outputfile) #FORMAT OUTPUT TO TABLE AND PRINT ON SCREEN
    #--------------------------------------------------------------

    #[OK]

elif(killsession == "sleep" and target_user == "" and server_option != "" and login_user != "" and password != ""): #KILL ALL SLEEPING SESSIONS OF ALL USERS ON ALL MENTIONED SERVERS 
    
    kill_all_sleep_session(server_option, outputkill, errorkill, login_user, password)

    #TO PRINT THE OUTPUT STATUS FOR ALL SESSIONS IRRESPECTIVE OF USER
    all_session_status(server_option, login_user, password, outputfile, errorfile) #EXECUTE THE COMMAND TO GET R/S ALL SESSIONS STATUS
    tableFormatOutput(server_option, outputfile) #FORMAT OUTPUT TO TABLE AND PRINT ON SCREEN
    #--------------------------------------------------------------

    print("")
    print("DONE")
    #[OK]

elif( status_arg == "all" and server_option != "" and login_user != "" and password != ""): #GET ALL SLEEPING/RUNNING SESSIONS INFORMATION
    
    all_session_status(server_option, login_user, password, outputfile, errorfile) #EXECUTE THE COMMAND TO GET R/S ALL SESSIONS STATUS
    tableFormatOutput(server_option, outputfile) #FORMAT OUTPUT TO TABLE AND PRINT ON SCREEN
    #[OK]

else:
    print("")
    print("Please provide the correct/complete arguments [Find the Below Help]")
    print("")
    help_function()
    sys.exit(2)

#===================================================================================================================================================================