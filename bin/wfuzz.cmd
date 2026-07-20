@echo off
REM WSL Kali wrapper for wfuzz
wsl -d kali-linux wfuzz %*
