@echo off
REM WSL Kali wrapper for nikto
wsl -d kali-linux nikto %*
