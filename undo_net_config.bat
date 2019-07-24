TIMEOUT 3
@echo resetting ipv4 to dhcp
netsh interface ip set address Wi-Fi dhcp
@echo disconnecting from Wi-Fi network
netsh wlan disconnect
@echo disconnected from Wi-Fi network
@echo process complete
pause

