#!/bin/sh
# Prüft ob gitbot läuft.
pgrep -fl gitbot.py > /dev/null 2>&1 || python /home/pbeck/gitbot/gitbot.py

