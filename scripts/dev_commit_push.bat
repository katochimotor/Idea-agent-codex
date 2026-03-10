@echo off
setlocal

git add .
git commit -m "dev update: %date% %time%"
git push
