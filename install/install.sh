#!/usr/bin/env bash
echo "create a aiogram service ..."
cp aiogram.sh /etc/systemd/system/aiogram
cp aiogram.service /etc/systemd/system
chmod +x /etc/systemd/system/aiogram
# sed -i "s/ykrasilnikov/upscaler-bot/src/g" /etc/systemd/system/aiogram
echo "created the aiogram service"