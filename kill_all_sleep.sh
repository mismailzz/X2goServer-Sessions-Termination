#!/bin/bash

sudo /sbin/x2golistsessions_root | awk '{split($0,a,"|"); print a[2],a[5]}' | grep -w S | awk '{split($0,a," "); print a[1]}' > sleep.txt
while read line; do
echo /bin/x2goterminate-session $line
sudo /bin/x2goterminate-session $line
sleep 1
done < sleep.txt
rm -f sleep.txt
