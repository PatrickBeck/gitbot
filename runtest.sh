#!/bin/sh
# Prüft ob gitbot läuft.
if [ $(ps aux | grep -c 'python gitbot.py') = 0 ];
then
    echo "$(date) gitbot abgestürzt, neu starten"
    python gitbot.py
fi

