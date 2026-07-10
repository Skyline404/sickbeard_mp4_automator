#!/bin/bash
# Wrapper script for qBittorrent to only process specific categories or folders

CONTENT_PATH="$1"
CATEGORY="$2"

# Если категория торрента "Anime" или "Movies", ИЛИ если путь содержит папку "Anime" или "Movies"
if [[ "$CATEGORY" == "Anime" || "$CATEGORY" == "Movies" || "$CONTENT_PATH" == *"Anime"* || "$CONTENT_PATH" == *"Movies"* || "$CONTENT_PATH" == *"TV"* ]]; then
    echo "Processing valid media: $CONTENT_PATH (Category: $CATEGORY)" >> /home/andrey/Lab/git/sickbeard_mp4_automator/wrapper_log.txt
    /home/andrey/Lab/git/sickbeard_mp4_automator/venv/bin/python /home/andrey/Lab/git/sickbeard_mp4_automator/manual.py -a -pa "/home/andrey/Lab/git/sickbeard_mp4_automator/processed_files.txt" -i "$CONTENT_PATH"
else
    echo "Skipping non-media torrent: $CONTENT_PATH (Category: $CATEGORY)" >> /home/andrey/Lab/git/sickbeard_mp4_automator/wrapper_log.txt
fi
