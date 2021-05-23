#!/bin/bash

target_user=mbutt05
X2GO_SESSION="$(echo "sudo /usr/sbin/x2golistsessions_root")"
AWK="$(echo "awk '{split(\$0,a,\"|\"); print a[2],a[12],a[5]}'")"
GREP="$(echo "grep -w --regexp='[S|R]'")"
USER="$(echo "grep -w $target_user")"
X2GO_SESSION_STATUS="$(echo "$X2GO_SESSION | $AWK | $GREP | $USER")"

if [[ $(eval $X2GO_SESSION_STATUS) ]]; then
    #SESSION=$(eval $X2GO_SESSION_STATUS)
	#The above statement makes list in one line string
	eval $X2GO_SESSION_STATUS > session_output.txt
	while read session_line; do
		echo $session_line | awk '{print $1","$2","$3}'
		
	done <session_output.txt
    #echo $SESSION | awk '{print $1","$2","$3}'
else
    echo "No Session Created Here"
fi
