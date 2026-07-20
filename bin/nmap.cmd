@echo off
REM WSL Kali wrapper for nmap
wsl -d kali-linux nmap %*
