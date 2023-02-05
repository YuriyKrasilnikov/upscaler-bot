#!/usr/bin/env bash
echo "uninstalling aiogram service ..."
unlink /etc/systemd/system/aiogram
unlink /etc/systemd/system/aiogram.service
echo "end"