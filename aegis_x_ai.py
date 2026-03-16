import nmap
import json
import os
import openai
import socket
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# DATABASE PROFESSIONALE ESPANSO (Esempi di vulnerabilità critiche reali)
VULN_DB = {
    "21": {"title": "VSFTPD 2.3.4 Backdoor RCE", "description": "Malicious backdoor in FTP source code allowing root access.", "exploit": "PoC: telnet <target> 21 -> USER user:)\nPASS pass", "mitigation": "Update to VSFTPD 3.0.5 or use SFTP."},
    "22": {"title": "SSH User Enumeration & Brute-Force", "description": "Legacy SSH version vulnerable to credential testing.", "exploit": "PoC: hydra -L users.txt -P rockyou.txt ssh://<target>", "mitigation": "Enforce SSH Keys & Fail2Ban."},
    "23": {"title": "Telnet Cleartext Vulnerability", "description": "Unencrypted management protocol.", "exploit": "PoC: Sniff traffic on port 23 to capture passwords.", "mitigation": "Disable Telnet, use SSH."},
    "25": {"title": "SMTP User Enumeration (VRFY)", "description": "Service allows harvesting valid system accounts.", "exploit": "PoC: smtp-user-enum -M VRFY -U users.txt -t <target>", "mitigation": "Disable VRFY/EXPN in SMTP config."},
    "80": {"title": "Web Server Vulnerability (HTTP)", "description": "Potential RCE, SQLi or Directory Traversal.", "exploit": "PoC: nikto -h http://<target>", "mitigation": "Update Web Server & Use WAF."},
    "445": {"title": "SMB Remote Code Execution (EternalBlue/Samba)", "description": "Critical flaw in SMB protocol handling.", "exploit": "PoC: Metasploit 'exploit/windows/smb/ms17_010_eternalblue' or 'trans2open'.", "mitigation": "Disable SMBv1. Apply MS17-010 or Samba patches."},
    "3306": {"title": "MySQL Remote Root Access", "description": "Database exposed with weak or no password.", "exploit": "PoC: mysql -u root -h <target>", "mitigation": "Bind to 127.0.0.1 & Set strong DB password."},
    "3389": {"title": "RDP BlueKeep / Brute-Force", "description": "Remote Desktop vulnerable to RCE or credential stuffing.", "exploit": "PoC: Use 'nmap --script rdp-vuln-ms12-020'.", "mitigation": "Enable NLA & Patch RDP."},
}

def print_cyber_banner():
    banner = rf"""
{Fore.RED}      ###    ########  ######   ####  ######            ##     ## 
{Fore.RED}     ## ##   ##       ##    ##   ##  ##    ##            ##   ##  
{Fore.RED}    ##   ##  ##       ##         ##  ##                   ## ##   
{Fore.WHITE}   ##     ## ######   ##   ####  ##   ######    #######    ###    
{Fore.WHITE}   ######### ##       ##    ##   ##        ##             ## ##   
{Fore.WHITE}   ##     ## ##       ##    ##   ##  ##    ##            ##   ##  
{Fore.WHITE}   ##     ## ########  ######   ####  ######            ##     ## 

{Fore.CYAN}   [+-------------------------------------------------------------+]
{Fore.CYAN}   [|  {Fore.YELLOW}AEGIS-X AI: FULL-SPECTRUM OFFENSIVE FRAMEWORK        {Fore.CYAN}      |]
{Fore.CYAN}   [|  {Fore.WHITE}Mission: Autonomous Infrastructure Security Auditing {Fore.CYAN}       |]
{Fore.CYAN}   [+-------------------------------------------------------------+]
    """
    print(banner)

class AegisXAI:
    def __init__(self, target):
        self.target = target
        self.nm = nmap.PortScanner()
        self.results = {"target": target, "start_time": "", "os": "Unknown", "hosts": []}

    def run_scan(self):
        print(f"{Fore.YELLOW}[*] Target Engaged: {self.target}")
        print(f"{Fore.CYAN}[*] Starting FULL 65535 Port Scan... This may take time.")
        self.results["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # SCANSIONE COMPLETA: -p- (tutte le porte), -sV (versioni), -O (OS detection)
        args = '-p- -sV -sC -O -Pn --version-intensity 8 -T4 --script vuln'
        self.nm.scan(self.target, arguments=args)

        for host in self.nm.all_hosts():
            os_match = self.nm[host].get('osmatch', [{'name': 'Unknown'}])[0]['name']
            host_data = {"ip": host, "os": os_match, "ports": []}
            print(f"{Fore.GREEN}[+] Host: {host} | OS: {os_match}")

            for proto in self.nm[host].all_protocols():
                for port in sorted(self.nm[host][proto].keys()):
                    svc = self.nm[host][proto][port]
                    print(f"    {Fore.GREEN}[FOUND] Port {port}...")
                    
                    vuln_info = VULN_DB.get(str(port), {
                        "title": f"Service Analysis: {svc['name'].upper()}",
                        "description": f"Identified {svc['name']} version {svc['version']}.",
                        "exploit": "Manual CVE lookup: 'searchsploit " + svc['name'] + " " + svc['version'] + "'",
                        "mitigation": "Ensure service is updated and restricted by firewall."
                    })

                    host_data["ports"].append({
                        "port": port, "service": svc['name'], "version": svc['version'], "details": vuln_info
                    })
            self.results["hosts"].append(host_data)

    def generate_html(self):
        fname = f"Audit_Report_{self.target}.html"
        h_logo = r"""
          _      _____  _____ _____  _____         __   __
         / \    |  ___|/ ____|_   _|/ ____|        \ \ / /
        / _ \   | |__ | |  __  | | | (___    ______ \ V / 
       / ___ \  |  __|| | |_ | | |  \___ \  |______| > <  
      / /   \ \ | |___| |__| |_| |_ ____) |         / ^ \ 
     /_/     \_\|______\_____|_____|_____/         /_/ \_\ 
        """
        html = f"""
        <html><head><title>Aegis-X Audit Report</title>
        <link rel='stylesheet' href='https://bootswatch.com/4/lux/bootstrap.min.css'>
        <style>
            body {{ background-color: #080808; color: #eee; font-family: monospace; }}
            .target-header {{ background: #000; color: #ff3333; padding: 40px; border-bottom: 5px solid #ff0000; }}
            .ascii-logo {{ color: #ff0000; font-family: monospace; white-space: pre; font-size: 12px; }}
            .vuln-card {{ background: #121212; margin-bottom: 40px; border: 1px solid #ff0000; }}
            pre {{ background: #000; color: #32ff32; padding: 15px; border: 1px solid #333; }}
            .mitigation-box {{ background: #0a1a0a; border-left: 5px solid #00ff00; padding: 15px; color: #00ff00; }}
        </style></head><body class='p-5'><div class='target-header text-center'>
        <pre class='ascii-logo'>{h_logo}</pre><h1>INFRASTRUCTURE AUDIT</h1>
        <p>Host: {self.target} | Date: {self.results['start_time']}</p></div><div class='container mt-5'>
        """
        for h in self.results["hosts"]:
            html += f"<h2 class='text-danger'>Target OS: {h['os']}</h2>"
            for p in h["ports"]:
                html += f"""
                <div class='card vuln-card'><div class='card-header bg-dark'><h4 style='color:#ff0000;'>PORT {p['port']} // {p['service'].upper()}</h4></div>
                <div class='card-body'><h5 class='text-white'>{p['details']['title']}</h5><p class='text-muted'>Version: {p['version']}</p>
                <p>{p['details']['description']}</p><p class='text-danger font-weight-bold'>EXPLOIT VECTOR:</p><pre>{p['details']['exploit']}</pre>
                <div class='mitigation-box'><strong>REMEDIATION:</strong><br>{p['details']['mitigation']}</div></div></div>
                """
        html += "</div></body></html>"
        with open(fname, "w") as f: f.write(html)
        print(f"\n[+] Full Audit Generated: {fname}")

if __name__ == "__main__":
    print_cyber_banner()
    t = input("Target IP: ")
    engine = AegisXAI(t)
    engine.run_scan()
    engine.generate_html()
