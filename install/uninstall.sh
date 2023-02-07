#!/usr/bin/env bash
echo "uninstalling aiogram service ..."
rm /etc/systemd/system/aiogram
rm /etc/systemd/system/aiogram.service
echo "end"