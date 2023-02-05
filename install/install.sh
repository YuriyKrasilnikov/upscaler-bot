#!/usr/bin/env bash
echo "create a aiogram service ..."
ln -s aiogram.sh /etc/systemd/system/aiogram
ln -s aiogram.service /etc/systemd/system
chmod +x /etc/systemd/system/aiogram
# sed -i "s/ykrasilnikov/upscaler-bot/src/g" /etc/systemd/system/aiogram
echo "created the aiogram service"