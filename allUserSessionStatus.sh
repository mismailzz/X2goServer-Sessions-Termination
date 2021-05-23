#!/bin/bash

X2GO_SESSION="$(echo "sudo /usr/sbin/x2golistsessions_root")"
AWK="$(echo "awk '{split(\$0,a,\"|\"); print a[2],a[12],a[5]}'")"
GREP="$(echo "grep -w --regexp='[S|R]'")"
X2GO_SESSION_STATUS="$(echo "$X2GO_SESSION | $AWK | $GREP")"

if [[ $(eval $X2GO_SESSION_STATUS) ]]; then
    #SESSION=$(eval $X2GO_SESSION_STATUS)
    #echo $SESSION 
    echo $( eval $X2GO_SESSION_STATUS  | awk '{print $1","$2","$3}' > sessionInfo)
    cat sessionInfo
    rm -f sessionInfo
else
    echo "No Session Created Here"
fi

