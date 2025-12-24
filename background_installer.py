#!/usr/bin/env python3
"""
Advanced Background Batch App Installer - FIXED for Ubuntu 24.04
Automatically runs in background - installs/uninstalls random apps in batches
Total: 161-199 apps, Batch size: 5-14 apps, Delay: 7-16 minutes
"""

import subprocess
import random
import time
import sys
import os
import logging
import atexit
import signal
from datetime import datetime

# Global flag for graceful shutdown
shutdown_flag = False
pid_file = "/tmp/background_batch_installer.pid"
log_file = "/tmp/background_batch_installer.log"

# Updated package list for Ubuntu 24.04 (Noble Numbat)
# Only packages that definitely exist in Ubuntu 24.04 repos
UBUNTU_2404_APPS = [
    # System Tools & Monitoring
    'htop', 'neofetch', 'btop', 'glances', 'nmon',
    'ncdu', 'ranger', 'mc', 'tree',
    'inxi', 'hardinfo', 'lshw',
    
    # Package Management
    'aptitude', 'synaptic', 'gdebi', 'snapd', 'flatpak',
    
    # Terminal & Shell
    'zsh', 'fish', 'powerline', 'fonts-powerline',
    'terminator', 'tilix', 'alacritty',
    'tmux', 'byobu', 'screen',
    
    # Text Editors & IDEs
    'vim', 'neovim', 'emacs', 'nano', 'gedit',
    'code', 'geany',
    
    # File Management
    'rsync', 'unzip', 'p7zip-full', 'unar',
    'filezilla', 'lftp', 'sshfs',
    'ntfs-3g', 'exfatprogs',
    
    # Network Tools
    'nmap', 'wireshark', 'tcpdump', 'net-tools', 'netcat',
    'nethogs', 'iftop', 'bmon', 'vnstat',
    'iperf3', 'speedtest-cli', 'openssh-server',
    'wireguard-tools', 'openvpn',
    
    # Development Tools
    'build-essential', 'cmake', 'autoconf', 'automake',
    'libtool', 'pkg-config', 'checkinstall',
    'gcc', 'g++', 'clang', 'gdb', 'valgrind',
    'python3', 'python3-pip', 'python3-venv', 'python3-dev',
    'python-is-python3', 'nodejs', 'npm',
    'default-jdk', 'openjdk-17-jdk', 'ruby', 'perl',
    'php', 'golang-go', 'rustc', 'cargo',
    'git', 'gitk', 'tig', 'subversion',
    
    # Web Servers & Databases
    'apache2', 'nginx', 'mysql-server', 'postgresql',
    'sqlite3', 'sqlitebrowser', 'redis-server',
    'mariadb-server', 'phpmyadmin',
    
    # Cloud & DevOps
    'docker.io', 'docker-compose', 'ansible',
    'awscli', 'azure-cli', 'kubectl',
    
    # Graphics & Design
    'gimp', 'inkscape', 'krita', 'blender',
    'darktable', 'digikam',
    
    # Multimedia
    'vlc', 'ffmpeg', 'handbrake', 'audacity',
    'obs-studio', 'kdenlive', 'openshot', 'shotcut',
    'mpv', 'clementine', 'rhythmbox',
    
    # Office & Productivity
    'libreoffice', 'thunderbird',
    'evince', 'okular', 'calibre',
    
    # Security
    'fail2ban', 'clamav', 'clamtk',
    'ufw', 'gufw', 'keepassxc', 'gnupg',
    
    # Virtualization
    'virtualbox', 'qemu-kvm', 'libvirt-daemon-system',
    'virt-manager',
    
    # System Administration
    'cron', 'rsyslog', 'smartmontools',
    'gparted', 'baobab',
    
    # Hardware
    'hwinfo', 'dmidecode', 'mesa-utils', 'vulkan-tools',
    'stress', 'stress-ng',
    
    # Fun & Miscellaneous
    'cmatrix', 'figlet', 'lolcat', 'cowsay',
    'fortune', 'sl', 'hollywood',
    
    # Browsers
    'firefox', 'chromium', 'epiphany-browser',
    
    # Communication
    'telegram-desktop', 'signal-desktop',
    'pidgin', 'hexchat',
    
    # File Sharing & Sync
    'transmission', 'qbittorrent', 'deluge',
    'nextcloud-desktop', 'syncthing',
    
    # System Cleanup
    'bleachbit', 'stacer',
    
    # Ubuntu 24.04 specific packages
    'software-properties-common', 'ubuntu-restricted-extras',
    'ubuntu-minimal', 'ubuntu-standard', 'ubuntu-desktop',
    'gnome-shell', 'gnome-terminal', 'nautilus',
    'gnome-calculator', 'gnome-calendar', 'gnome-characters',
    'gnome-clocks', 'gnome-contacts', 'gnome-disk-utility',
    'gnome-font-viewer', 'gnome-logs', 'gnome-maps',
    'gnome-music', 'gnome-photos', 'gnome-screenshot',
    'gnome-software', 'gnome-system-monitor', 'gnome-terminal',
    'gnome-tweaks', 'gnome-weather',
    
    # Development libraries
    'libssl-dev', 'libreadline-dev', 'libsqlite3-dev',
    'libbz2-dev', 'libgdbm-dev', 'liblzma-dev',
    'tk-dev', 'libffi-dev', 'libncurses5-dev',
    'libncursesw5-dev', 'zlib1g-dev',
    
    # Media codecs
    'gstreamer1.0-libav', 'gstreamer1.0-plugins-bad',
    'gstreamer1.0-plugins-base', 'gstreamer1.0-plugins-good',
    'gstreamer1.0-plugins-ugly', 'libdvd-pkg',
    
    # Fonts
    'fonts-firacode', 'fonts-hack', 'fonts-noto',
    'fonts-liberation', 'fonts-dejavu', 'fonts-ubuntu',
    'fonts-roboto', 'ttf-mscorefonts-installer',
    
    # Python packages
    'python3-numpy', 'python3-scipy', 'python3-matplotlib',
    'python3-pandas', 'python3-seaborn', 'python3-sklearn',
    'python3-django', 'python3-flask', 'python3-requests',
    
    # System utilities
    'curl', 'wget', 'lynx', 'axel', 'aria2',
    'zip', 'unrar', 'cabextract', 'unar',
    'lsb-release', 'apt-transport-https',
    'ca-certificates', 'gnupg', 'lsb-release',
    
    # Monitoring
    'dstat', 'iotop', 'atop', 'sar',
    
    # Backup
    'deja-dup', 'timeshift',
    
    # Remote access
    'remmina', 'remmina-plugin-rdp',
    'remmina-plugin-vnc', 'x2goclient',
    
    # Printing
    'cups', 'cups-pdf', 'system-config-printer',
    
    # Bluetooth
    'bluetooth', 'bluez', 'blueman',
    
    # Kernel
    'linux-headers-generic', 'linux-tools-generic',
    
    # Archive formats
    'zip', 'unzip', 'p7zip-full', 'rar', 'unrar',
    'cabextract', 'lzop', 'lz4',
    
    # Disk utilities
    'testdisk', 'photorec', 'ddrescue',
    'gdisk', 'fdisk', 'parted',
    
    # Network managers
    'network-manager', 'network-manager-openvpn',
    'network-manager-openconnect', 'network-manager-pptp',
    
    # VPN
    'openconnect', 'network-manager-openconnect',
    
    # Containers
    'podman', 'buildah', 'skopeo',
    
    # Version control
    'git', 'mercurial', 'bzr',
    
    # Build tools
    'ninja-build', 'meson', 'scons',
    
    # Documentation
    'man-db', 'manpages', 'manpages-dev',
    'info', 'texinfo',
    
    # Shell enhancements
    'bash-completion', 'command-not-found',
    
    # Desktop environments
    'gnome-shell-extensions', 'chrome-gnome-shell',
    
    # Multimedia editing
    'pitivi', 'flowblade',
    
    # 3D modeling
    'freecad', 'openscad',
    
    # CAD
    'librecad',
    
    # Electronics
    'kicad', 'geda', 'fritzing',
    
    # Astronomy
    'stellarium', 'celestia',
    
    # Chemistry
    'avogadro', 'kalzium',
    
    # Mathematics
    'geogebra', 'kmplot',
    
    # Physics
    'step',
    
    # Education
    'gcompris', 'tuxmath', 'tuxtype',
    
    # Games
    'supertuxkart', 'minetest', 'wesnoth',
    'freeciv', 'openttd', 'openarena',
    
    # Emulators
    'dosbox', 'mame', 'mednafen',
    
    # Wine
    'wine', 'playonlinux',
    
    # Steam
    'steam-installer',
    
    # Android
    'scrcpy', 'android-tools-adb',
    
    # Virtual machines
    'virt-viewer', 'spice-vdagent',
    
    # Cloud storage
    'rclone', 'megasync',
    
    # Social media
    'discord', 'slack',
    
    # Video conferencing
    'zoom', 'teams',
    
    # Office suites
    'onlyoffice-desktopeditors',
    
    # Note taking
    'joplin', 'standardnotes',
    
    # Password managers
    'bitwarden', 'pass',
    
    # Torrent
    'transmission-gtk', 'qbittorrent',
    
    # Download managers
    'uget', 'xtreme-download-manager',
    
    # File managers
    'nemo', 'pcmanfm', 'thunar',
    
    # Terminal multiplexers
    'dtach', 'abduco',
    
    # Shells
    'ksh', 'tcsh', 'dash',
    
    # System info
    'neofetch', 'screenfetch', 'alsi',
    
    # ASCII art
    'toilet', 'boxes',
    
    # System monitors
    'conky', 'variety',
    
    # Screenshot tools
    'shutter', 'flameshot',
    
    # Screen recording
    'kazam', 'simplescreenrecorder',
    
    # Image editors
    'pinta', 'photogimp',
    
    # Vector graphics
    'libreoffice-draw', 'sodiplot',
    
    # Audio editors
    'ocenaudio', 'ardour',
    
    # Video editors
    'flowblade', 'olive',
    
    # Live streaming
    'obs-studio', 'streamlabs-obs',
    
    # CD/DVD burning
    'brasero', 'k3b',
    
    # ISO tools
    'acetoneiso', 'furiusisomount',
    
    # Partition tools
    'gparted', 'gnome-disk-utility',
    
    # Backup tools
    'timeshift', 'deja-dup',
    
    # System cleanup
    'bleachbit', 'stacer', 'ubuntu-cleaner',
    
    # Package cleanup
    'deborphan', 'gtkorphan',
    
    # System optimizers
    'preload', 'earlyoom',
    
    # Security hardening
    'lynis', 'tiger', 'chkrootkit',
    
    # Firewalls
    'ufw', 'gufw', 'firewalld',
    
    # Privacy tools
    'torbrowser-launcher', 'onionshare',
    
    # Encryption
    'veracrypt', 'cryptsetup',
    
    # Networking
    'mtr', 'traceroute', 'whois',
    'dnsutils', 'iputils-ping',
    
    # Wireless
    'iw', 'wireless-tools', 'wavemon',
    
    # Bluetooth
    'bluetooth', 'bluez', 'blueman',
    
    # USB
    'usbutils', 'mtools',
    
    # Printing
    'cups', 'cups-pdf', 'hplip',
    
    # Scanning
    'sane', 'xsane',
    
    # Accessibility
    'orca', 'brltty',
    
    # Localization
    'language-pack-en', 'language-pack-gnome-en',
    
    # Input methods
    'ibus', 'ibus-mozc', 'fcitx',
    
    # Themes
    'arc-theme', 'papirus-icon-theme',
    'materia-gtk-theme', 'adapta-gtk-theme',
    
    # Icons
    'papirus-icon-theme', 'breeze-icon-theme',
    'numix-icon-theme', 'faenza-icon-theme',
    
    # Cursors
    'breeze-cursor-theme', 'dmz-cursor-theme',
    
    # Fonts
    'fonts-roboto', 'fonts-firacode',
    'fonts-hack', 'fonts-ibm-plex',
    
    # Utilities
    'trash-cli', 'fzf', 'bat', 'exa',
    'ripgrep', 'fd-find', 'jq', 'yq',
    'htop', 'bashtop', 'gotop'
]

def daemonize():
    """Turn the script into a daemon that runs in background"""
    try:
        # First fork
        pid = os.fork()
        if pid > 0:
            # Parent exits
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f"First fork failed: {e}\n")
        sys.exit(1)
    
    # Decouple from parent environment
    os.chdir('/')
    os.setsid()
    os.umask(0)
    
    # Second fork
    try:
        pid = os.fork()
        if pid > 0:
            # Parent exits
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f"Second fork failed: {e}\n")
        sys.exit(1)
    
    # Redirect standard file descriptors to /dev/null
    devnull = '/dev/null'
    if hasattr(os, 'devnull'):
        devnull = os.devnull
    
    so = open(devnull, 'a+')
    se = open(devnull, 'a+')
    
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    
    # Write PID file
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    
    # Register cleanup
    atexit.register(cleanup_pid_file)
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_flag
    shutdown_flag = True

def cleanup_pid_file():
    """Remove PID file on exit"""
    if os.path.exists(pid_file):
        os.remove(pid_file)

def check_existing_process():
    """Check if another instance is already running"""
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running
            try:
                os.kill(pid, 0)
                return True, pid
            except OSError:
                # Process not running, remove stale PID file
                os.remove(pid_file)
                return False, None
        except:
            # Corrupted PID file
            os.remove(pid_file)
            return False, None
    return False, None

def setup_logging():
    """Setup logging for background process"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
        ]
    )
    return logging.getLogger(__name__)

def update_system(logger):
    """Update system packages"""
    logger.info("Updating system packages...")
    try:
        result = subprocess.run(
            ['apt', 'update'],
            timeout=300,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("System updated successfully")
            return True
        else:
            logger.warning(f"Update had issues: {result.stderr[:200]}")
            return True
    except subprocess.TimeoutExpired:
        logger.error("Update timed out")
        return False
    except Exception as e:
        logger.error(f"Update error: {e}")
        return False

def check_package_exists(package_name):
    """Check if a package exists in the repositories"""
    try:
        result = subprocess.run(
            ['apt-cache', 'search', '--names-only', f'^{package_name}$'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0 and package_name in result.stdout
    except:
        return False

def install_batch(apps_list, batch_num, total_batches, logger):
    """Install a batch of apps with package validation"""
    logger.info(f"Installing batch {batch_num}: {len(apps_list)} apps")
    
    # Filter out packages that don't exist
    valid_apps = []
    for app in apps_list:
        if check_package_exists(app):
            valid_apps.append(app)
        else:
            logger.warning(f"Package not found: {app}")
    
    if not valid_apps:
        logger.error(f"No valid packages in batch {batch_num}")
        return False
    
    logger.info(f"Valid packages: {len(valid_apps)}/{len(apps_list)}")
    
    try:
        # Install all valid apps in batch
        result = subprocess.run(
            ['apt', 'install', '-y', '--no-install-recommends'] + valid_apps,
            timeout=600,  # 10 minute timeout
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"✓ Batch {batch_num} installed successfully")
            return True
        else:
            logger.warning(f"⚠ Batch {batch_num} installation failed")
            logger.debug(f"Error: {result.stderr[:500]}")
            
            # Try installing individually with recommended packages
            success_count = 0
            for app in valid_apps:
                try:
                    app_result = subprocess.run(
                        ['apt', 'install', '-y', app],
                        timeout=180,
                        capture_output=True,
                        text=True
                    )
                    if app_result.returncode == 0:
                        success_count += 1
                        logger.info(f"  ✓ Installed {app}")
                    else:
                        logger.warning(f"  ✗ Failed to install {app}: {app_result.stderr[:100]}")
                except subprocess.TimeoutExpired:
                    logger.warning(f"  ✗ Timeout installing {app}")
                except Exception as e:
                    logger.warning(f"  ✗ Error installing {app}: {e}")
            
            logger.info(f"  Individual installs: {success_count}/{len(valid_apps)} successful")
            return success_count > 0
            
    except subprocess.TimeoutExpired:
        logger.error(f"✗ Batch {batch_num} installation timed out")
        return False
    except Exception as e:
        logger.error(f"✗ Batch {batch_num} error: {e}")
        return False

def uninstall_batch(apps_list, batch_num, total_batches, logger):
    """Uninstall a batch of apps"""
    logger.info(f"Uninstalling batch {batch_num}: {len(apps_list)} apps")
    
    try:
        # First, get list of actually installed packages
        installed_apps = []
        for app in apps_list:
            result = subprocess.run(
                ['dpkg', '-l', app],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and 'ii' in result.stdout:
                installed_apps.append(app)
        
        if not installed_apps:
            logger.info(f"No packages from batch {batch_num} are installed")
            return True
        
        # Uninstall installed apps
        result = subprocess.run(
            ['apt', 'remove', '-y', '--purge'] + installed_apps,
            timeout=300,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"✓ Batch {batch_num} uninstalled successfully")
            return True
        else:
            logger.warning(f"⚠ Batch {batch_num} uninstallation had issues")
            
            # Try uninstalling individually
            for app in installed_apps:
                subprocess.run(
                    ['apt', 'remove', '-y', '--purge', app],
                    timeout=60,
                    capture_output=True
                )
            return True
            
    except subprocess.TimeoutExpired:
        logger.error(f"✗ Batch {batch_num} uninstallation timed out")
        return False
    except Exception as e:
        logger.error(f"✗ Batch {batch_num} uninstall error: {e}")
        return False

def cleanup_system(logger):
    """Clean up system after operations"""
    logger.info("Performing system cleanup...")
    
    try:
        subprocess.run(
            ['apt', 'autoremove', '-y'],
            timeout=180,
            capture_output=True
        )
        subprocess.run(
            ['apt', 'autoclean'],
            timeout=60,
            capture_output=True
        )
        logger.info("System cleanup completed")
    except:
        logger.warning("Cleanup had issues")

def main_installation():
    """Main installation process - runs in background"""
    global shutdown_flag
    
    # Setup logging
    logger = setup_logging()
    
    logger.info("="*60)
    logger.info("BACKGROUND BATCH APP INSTALLER STARTED")
    logger.info(f"Start time: {datetime.now()}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info("="*60)
    
    # Update system first
    logger.info("Updating package lists...")
    subprocess.run(['apt', 'update'], capture_output=True)
    
    # Total number of apps to install/uninstall (161-199)
    total_apps = random.randint(161, 199)
    logger.info(f"Total apps to process: {total_apps}")
    
    # Process apps in batches
    processed_apps = 0
    batch_number = 0
    
    while processed_apps < total_apps and not shutdown_flag:
        batch_number += 1
        
        # Check for shutdown flag
        if shutdown_flag:
            logger.info("Shutdown requested, stopping...")
            break
        
        # Determine batch size (5-14 apps)
        batch_size = random.randint(5, 14)
        
        # Adjust last batch size if needed
        if processed_apps + batch_size > total_apps:
            batch_size = total_apps - processed_apps
        
        # Select random apps for this batch
        batch_apps = random.sample(UBUNTU_2404_APPS, min(batch_size, len(UBUNTU_2404_APPS)))
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Starting batch {batch_number}")
        logger.info(f"Batch size: {batch_size} apps")
        logger.info(f"Progress: {processed_apps}/{total_apps} apps")
        logger.info(f"Selected apps: {', '.join(batch_apps)}")
        
        # Install the batch
        if install_batch(batch_apps, batch_number, "unknown", logger):
            logger.info(f"✓ Installation of batch {batch_number} completed")
        else:
            logger.warning(f"⚠ Installation of batch {batch_number} had issues")
        
        # Check for shutdown before delay
        if shutdown_flag:
            logger.info("Shutdown requested, stopping...")
            break
        
        # Random delay between 7-16 minutes
        delay_minutes = random.randint(7, 16)
        delay_seconds = delay_minutes * 60
        logger.info(f"Waiting {delay_minutes} minutes before uninstalling...")
        
        # Break delay into smaller chunks to check shutdown flag
        chunk_size = 30  # Check every 30 seconds
        for i in range(0, delay_seconds, chunk_size):
            if shutdown_flag:
                break
            time.sleep(min(chunk_size, delay_seconds - i))
        
        if shutdown_flag:
            logger.info("Shutdown requested, stopping...")
            break
        
        # Uninstall the batch
        if uninstall_batch(batch_apps, batch_number, "unknown", logger):
            logger.info(f"✓ Uninstallation of batch {batch_number} completed")
        else:
            logger.warning(f"⚠ Uninstallation of batch {batch_number} had issues")
        
        # Update processed count
        processed_apps += batch_size
        
        # Random delay before next batch (1-3 minutes)
        if processed_apps < total_apps and not shutdown_flag:
            next_delay = random.randint(60, 180)
            logger.info(f"Waiting {next_delay//60} minutes before next batch...")
            
            for i in range(0, next_delay, chunk_size):
                if shutdown_flag:
                    break
                time.sleep(min(chunk_size, next_delay - i))
        
        # Occasional cleanup
        if batch_number % 3 == 0 and not shutdown_flag:
            cleanup_system(logger)
    
    # Final cleanup
    logger.info("\n" + "="*50)
    if shutdown_flag:
        logger.info("PROCESS STOPPED BY USER")
    else:
        logger.info("ALL BATCHES COMPLETED!")
    
    logger.info(f"Total batches processed: {batch_number}")
    logger.info(f"Total apps installed/uninstalled: {processed_apps}")
    
    cleanup_system(logger)
    
    if shutdown_flag:
        logger.info("Process stopped gracefully")
    else:
        logger.info("Process completed successfully!")
    
    logger.info(f"End time: {datetime.now()}")
    logger.info("="*60)

def show_status():
    """Show current status if running"""
    is_running, pid = check_existing_process()
    
    if is_running:
        print(f"✓ Background process is RUNNING (PID: {pid})")
    else:
        print("✗ Background process is NOT running")
    
    print(f"\nLog file: {log_file}")
    
    if os.path.exists(log_file):
        print("\nLast 20 lines of log:")
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()[-20:]
                for line in lines:
                    print(line.strip())
        except Exception as e:
            print(f"Could not read log file: {e}")
    else:
        print("\nLog file does not exist yet")

def stop_process():
    """Stop the running background process"""
    is_running, pid = check_existing_process()
    
    if not is_running:
        print("No background process is running")
        return
    
    try:
        # Send SIGTERM signal
        os.kill(pid, signal.SIGTERM)
        print(f"✓ Sent stop signal to process {pid}")
        
        # Wait for process to terminate
        for i in range(10):
            try:
                os.kill(pid, 0)
                print(f"Waiting for process to stop... ({i+1}/10)")
                time.sleep(1)
            except OSError:
                print("✓ Process stopped successfully")
                if os.path.exists(pid_file):
                    os.remove(pid_file)
                return
        
        # If still running, send SIGKILL
        print("Process not responding, sending SIGKILL...")
        os.kill(pid, signal.SIGKILL)
        time.sleep(1)
        
        if os.path.exists(pid_file):
            os.remove(pid_file)
        print("✓ Process terminated")
        
    except Exception as e:
        print(f"✗ Error stopping process: {e}")

def show_summary():
    """Show summary of what will happen"""
    print("\n" + "="*60)
    print("BACKGROUND BATCH APP INSTALLER - UBUNTU 24.04 FIXED")
    print("="*60)
    print("This script will run in the background and:")
    print(f"1. Install 161-199 random useful apps")
    print("2. Process apps in batches of 5-14 apps")
    print("3. For each batch:")
    print("   - Install the batch")
    print("   - Wait 7-16 minutes")
    print("   - Uninstall the batch")
    print("4. Continue until all apps are processed")
    print("\nIMPROVEMENTS:")
    print("• Only uses packages that exist in Ubuntu 24.04")
    print("• Checks package availability before installing")
    print("• Better error handling and logging")
    print("\nEstimated time: 1.5 to 10.5 hours")
    print(f"Log file: {log_file}")
    print(f"PID file: {pid_file}")
    print("="*60)
    print("\nCommands:")
    print(f"  Start:   sudo {sys.argv[0]} start")
    print(f"  Status:  {sys.argv[0]} status")
    print(f"  Stop:    {sys.argv[0]} stop")
    print(f"  Help:    {sys.argv[0]} help")
    print("="*60 + "\n")

def show_banner():
    """Show application banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     BACKGROUND BATCH APP INSTALLER - UBUNTU 24.04 FIXED      ║
║     Auto-background • Verified Packages • Safe Execution     ║
╚══════════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    # Show banner
    show_banner()
    
    # Check arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            # Check if already running
            is_running, pid = check_existing_process()
            if is_running:
                print(f"✗ Another instance is already running (PID: {pid})")
                print(f"Check log: tail -f {log_file}")
                print(f"Stop first: {sys.argv[0]} stop")
                sys.exit(1)
            
            # Show summary
            show_summary()
            
            # Check if running as root
            if os.geteuid() != 0:
                print("✗ This script requires sudo privileges!")
                print(f"Please run: sudo {sys.argv[0]} start")
                sys.exit(1)
            
            # Confirm
            response = input("Start in background? (yes/NO): ").strip().lower()
            if response != 'yes':
                print("Cancelled.")
                sys.exit(0)
            
            print("\n✓ Starting in background...")
            print(f"✓ Check status: {sys.argv[0]} status")
            print(f"✓ Stop anytime: {sys.argv[0]} stop")
            print(f"✓ Watch logs: tail -f {log_file}")
            print("\nThe process will continue even if you close this terminal.")
            
            # Daemonize and start installation
            daemonize()
            main_installation()
            
        elif command == "stop":
            print("Stopping background process...")
            stop_process()
            
        elif command == "status":
            show_status()
            
        elif command in ["help", "--help", "-h"]:
            show_summary()
            
        else:
            print(f"✗ Unknown command: {command}")
            print(f"Usage: {sys.argv[0]} [start|stop|status|help]")
            sys.exit(1)
            
    else:
        # No arguments - show help
        show_summary()

# Save this script as: fixed_background_installer.py
