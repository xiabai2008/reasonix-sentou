@echo off
REM WSL Kali wrapper for proxychains
wsl -d kali-linux proxychains4 %*
