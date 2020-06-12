#!/usr/bin/bash
cd "/C/Users/brian/AppData/Local/Google/Chrome SxS/Application"
./chrome.exe --headless --disable-gpu --remote-debugging-port=9222 $*
