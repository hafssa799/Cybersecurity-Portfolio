#!/bin/bash
# Custom Active Response - block Modbus attacker by src_ip
# Emplacement sur le routeur : /var/ossec/active-response/bin/modbus-block.sh
# Droits : chmod +x ; chown root:wazuh
read INPUT
IP=$(echo "$INPUT" | grep -oP "\"src_ip\":\"\K[0-9.]+" | head -1)
LOG="/var/ossec/logs/active-responses.log"

if [ -n "$IP" ]; then
    iptables -I FORWARD -s "$IP" -j DROP
    iptables -I INPUT -s "$IP" -j DROP
    echo "$(date +"%Y/%m/%d %H:%M:%S") modbus-block: BLOCKED attacker IP $IP" >> "$LOG"
else
    echo "$(date +"%Y/%m/%d %H:%M:%S") modbus-block: could not extract src_ip" >> "$LOG"
fi
