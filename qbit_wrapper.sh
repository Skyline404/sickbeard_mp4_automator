#!/bin/bash
# Wrapper script for qBittorrent to only process specific categories or folders

CONTENT_PATH="$1"
CATEGORY="$2"

if [[ "$CATEGORY" == "Anime" || "$CATEGORY" == "Movies" || "$CONTENT_PATH" == *"Anime"* || "$CONTENT_PATH" == *"Movies"* || "$CONTENT_PATH" == *"TV"* ]]; then
    echo "Processing valid media: $CONTENT_PATH (Category: $CATEGORY)" >> /home/andrey/Lab/git/sickbeard_mp4_automator/wrapper_log.txt
    
    # 1. Сначала добавляем таймкоды AniSkip (работает и для отдельных файлов, и для папок)
    echo "Running AniSkip adder..." >> /home/andrey/Lab/git/sickbeard_mp4_automator/wrapper_log.txt
    /home/andrey/Lab/git/sickbeard_mp4_automator/venv/bin/python /home/andrey/Lab/git/sickbeard_mp4_automator/aniskip_adder.py "$CONTENT_PATH" >> /home/andrey/Lab/git/sickbeard_mp4_automator/wrapper_log.txt 2>&1
    
    # 2. Затем вызываем штатный автоматизатор, который отсортирует, исправит контейнеры и перенесет
    /home/andrey/Lab/git/sickbeard_mp4_automator/venv/bin/python /home/andrey/Lab/git/sickbeard_mp4_automator/manual.py -a -pa "/home/andrey/Lab/git/sickbeard_mp4_automator/processed_files.json" -i "$CONTENT_PATH"
else
    echo "Skipping non-media torrent: $CONTENT_PATH (Category: $CATEGORY)" >> /home/andrey/Lab/git/sickbeard_mp4_automator/wrapper_log.txt
fi
