#!/bin/bash
#session_id="$1"
session_id=( "$@" )
for user_session in "${session_id[@]}"
do
	echo $user_session
	#echo sudo /bin/x2goterminate-session $user_session
	sudo /bin/x2goterminate-session $user_session
done

