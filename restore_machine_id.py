import os
import sys
import json
import uuid
import hashlib
import shutil
import sqlite3
import platform
import re
import glob
import tempfile
from colorama import Fore, Style, init
from typing import Tuple
import configparser
import traceback
from config import get_config
from datetime import datetime

# Import cac ham dung chung
from reset_machine_manual import get_cursor_machine_id_path, get_user_documents_path

# Khoi tao colorama
init()

# Dinh nghia emoji
EMOJI = {
    "FILE": "📄",
    "BACKUP": "💾",
    "SUCCESS": "✅",
    "ERROR": "❌",
    "INFO": "ℹ️",
    "RESET": "🔄",
    "WARNING": "⚠️",
}

class ConfigError(Exception):
    """Loi cau hinh"""
    pass

class MachineIDRestorer:
    def __init__(self, translator=None):
        self.translator = translator
        
        # Doc cau hinh
        config_dir = os.path.join(get_user_documents_path(), ".cursor-pro")
        config_file = os.path.join(config_dir, "config.ini")
        config = configparser.ConfigParser()
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        config.read(config_file, encoding='utf-8')
        
        # Dua tren
        if sys.platform == "win32":  # Windows
            appdata = os.getenv("APPDATA")
            if appdata is None:
                raise EnvironmentError("APPDATA Environment Variable Not Set")
            
            if not config.has_section('WindowsPaths'):
                raise ConfigError("WindowsPaths section not found in config")
                
            self.db_path = config.get('WindowsPaths', 'storage_path')
            self.sqlite_path = config.get('WindowsPaths', 'sqlite_path')
            
        elif sys.platform == "darwin":  # macOS
            if not config.has_section('MacPaths'):
                raise ConfigError("MacPaths section not found in config")
                
            self.db_path = config.get('MacPaths', 'storage_path')
            self.sqlite_path = config.get('MacPaths', 'sqlite_path')
            
        elif sys.platform == "linux":  # Linux
            if not config.has_section('LinuxPaths'):
                raise ConfigError("LinuxPaths section not found in config")
                
            self.db_path = config.get('LinuxPaths', 'storage_path')
            self.sqlite_path = config.get('LinuxPaths', 'sqlite_path')
            
        else:
            raise NotImplementedError(f"Not Supported OS: {sys.platform}")
    
    def find_backups(self):
        """Tim kiem cac file backup co san"""
        db_dir = os.path.dirname(self.db_path)
        db_name = os.path.basename(self.db_path)
        
        # Tim kiem file co dinh dang {db_name}.bak.{timestamp}
        backup_pattern = f"{db_name}.bak.*"
        backups = glob.glob(os.path.join(db_dir, backup_pattern))
        
        # Sap xep theo thoi gian (moi nhat truoc)
        backups.sort(key=os.path.getctime, reverse=True)
        
        return backups
    
    def list_backups(self):
        """Liet ke tat ca backup co san"""
        backups = self.find_backups()
        
        if not backups:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} {self.translator.get('restore.no_backups_found')}{Style.RESET_ALL}")
            return None
        
        print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('restore.available_backups')}:{Style.RESET_ALL}")
        for i, backup in enumerate(backups, 1):
            # Lay thong tin backup
            timestamp_str = backup.split('.')[-1]
            try:
                # Phan tich timestamp (dinh dang YYYYmmdd_HHMMSS)
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                date_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                date_str = "Khong xac dinh"
            
            # Lay kich thuoc file
            size = os.path.getsize(backup)
            size_str = f"{size / 1024:.1f} KB"
            
            print(f"{i}. {Fore.GREEN}{os.path.basename(backup)}{Style.RESET_ALL} ({date_str}, {size_str})")
        
        return backups
    
    def select_backup(self):
        """Cho nguoi dung chon backup de phuc hoi"""
        backups = self.list_backups()
        
        if not backups:
            return None
        
        while True:
            try:
                choice = input(f"{EMOJI['INFO']} {self.translator.get('restore.select_backup')} (1-{len(backups)}, 0 {self.translator.get('restore.to_cancel')}): ")
                
                if choice.strip() == '0':
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('restore.operation_cancelled')}{Style.RESET_ALL}")
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(backups):
                    return backups[index]
                else:
                    print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.invalid_selection')}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.please_enter_number')}{Style.RESET_ALL}")
    
    def extract_ids_from_backup(self, backup_path):
        """Trich xuat Machine ID tu backup file"""
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_data = json.load(f)
            
            # Trich xuatID
            ids = {
                "telemetry.devDeviceId": backup_data.get("telemetry.devDeviceId", ""),
                "telemetry.macMachineId": backup_data.get("telemetry.macMachineId", ""),
                "telemetry.machineId": backup_data.get("telemetry.machineId", ""),
                "telemetry.sqmId": backup_data.get("telemetry.sqmId", ""),
                "storage.serviceMachineId": backup_data.get("storage.serviceMachineId", 
                                                          backup_data.get("telemetry.devDeviceId", ""))
            }
            
            # Dam bao tat ca ID deu ton tai
            for key, value in ids.items():
                if not value:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} {self.translator.get('restore.missing_id', id=key)}{Style.RESET_ALL}")
            
            return ids
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.read_backup_failed', error=str(e))}{Style.RESET_ALL}")
            return None
    
    def update_current_file(self, ids):
        """Cap nhat file storage.json hien tai"""
        try:
            if not os.path.exists(self.db_path):
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.current_file_not_found')}: {self.db_path}{Style.RESET_ALL}")
                return False
            
            # Doc file hien tai
            with open(self.db_path, "r", encoding="utf-8") as f:
                current_data = json.load(f)
            
            # Tao backup file hien tai
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.db_path}.restore_bak.{timestamp}"
            shutil.copy2(self.db_path, backup_path)
            print(f"{Fore.GREEN}{EMOJI['BACKUP']} {self.translator.get('restore.current_backup_created')}: {backup_path}{Style.RESET_ALL}")
            
            # Cap nhat cac ID
            current_data.update(ids)
            
            # Luu file da cap nhat
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(current_data, f, indent=4)
            
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('restore.storage_updated')}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.update_failed', error=str(e))}{Style.RESET_ALL}")
            return False
    
    def update_sqlite_db(self, ids):
        """Cap nhat ID trong SQLite database"""
        try:
            if not os.path.exists(self.sqlite_path):
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.sqlite_not_found')}: {self.sqlite_path}{Style.RESET_ALL}")
                return False
            
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('restore.updating_sqlite')}...{Style.RESET_ALL}")
            
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ItemTable (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            
            for key, value in ids.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO ItemTable (key, value) 
                    VALUES (?, ?)
                """, (key, value))
                print(f"{EMOJI['INFO']} {Fore.CYAN} {self.translator.get('restore.updating_pair')}: {key}{Style.RESET_ALL}")
            
            conn.commit()
            conn.close()
            
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('restore.sqlite_updated')}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.sqlite_update_failed', error=str(e))}{Style.RESET_ALL}")
            return False
    
    def update_machine_id_file(self, dev_device_id):
        """Cap nhat file machineId"""
        try:
            machine_id_path = get_cursor_machine_id_path(self.translator)
            
            # Tao thu muc neu chua ton tai
            os.makedirs(os.path.dirname(machine_id_path), exist_ok=True)
            
            # Tao backup file hien tai neu ton tai
            if os.path.exists(machine_id_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{machine_id_path}.restore_bak.{timestamp}"
                try:
                    shutil.copy2(machine_id_path, backup_path)
                    print(f"{Fore.GREEN}{EMOJI['INFO']} {self.translator.get('restore.machine_id_backup_created')}: {backup_path}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('restore.backup_creation_failed', error=str(e))}{Style.RESET_ALL}")
            
            # Ghi Machine ID moi
            with open(machine_id_path, "w", encoding="utf-8") as f:
                f.write(dev_device_id)
            
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('restore.machine_id_updated')}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.machine_id_update_failed', error=str(e))}{Style.RESET_ALL}")
            return False
    
    def update_system_ids(self, ids):
        """Cap nhat cac ID he thong"""
        try:
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('restore.updating_system_ids')}...{Style.RESET_ALL}")
            
            if sys.platform.startswith("win"):
                self._update_windows_system_ids(ids)
            elif sys.platform == "darwin":
                self._update_macos_system_ids(ids)
            
            return True
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.system_ids_update_failed', error=str(e))}{Style.RESET_ALL}")
            return False
    
    def _update_windows_system_ids(self, ids):
        """Cap nhat Windows system ID"""
        try:
            import winreg
            
            # Cap nhat MachineGuid
            guid = ids.get("telemetry.devDeviceId", "")
            if guid:
                try:
                    key = winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        "SOFTWARE\\Microsoft\\Cryptography",
                        0,
                        winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
                    )
                    winreg.SetValueEx(key, "MachineGuid", 0, winreg.REG_SZ, guid)
                    winreg.CloseKey(key)
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('restore.windows_machine_guid_updated')}{Style.RESET_ALL}")
                except PermissionError:
                    print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.permission_denied')}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.update_windows_machine_guid_failed', error=str(e))}{Style.RESET_ALL}")
            
            # Cap nhat SQMClient MachineId
            sqm_id = ids.get("telemetry.sqmId", "")
            if sqm_id:
                try:
                    key = winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        r"SOFTWARE\Microsoft\SQMClient",
                        0,
                        winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
                    )
                    winreg.SetValueEx(key, "MachineId", 0, winreg.REG_SZ, sqm_id)
                    winreg.CloseKey(key)
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('restore.windows_machine_id_updated')}{Style.RESET_ALL}")
                except FileNotFoundError:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} {self.translator.get('restore.sqm_client_key_not_found')}{Style.RESET_ALL}")
                except PermissionError:
                    print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.permission_denied')}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.update_windows_machine_id_failed', error=str(e))}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.update_windows_system_ids_failed', error=str(e))}{Style.RESET_ALL}")
    
    def _update_macos_system_ids(self, ids):
        """Cap nhat macOS system ID"""
        try:
            uuid_file = "/var/root/Library/Preferences/SystemConfiguration/com.apple.platform.uuid.plist"
            if os.path.exists(uuid_file):
                mac_id = ids.get("telemetry.macMachineId", "")
                if mac_id:
                    cmd = f'sudo plutil -replace "UUID" -string "{mac_id}" "{uuid_file}"'
                    result = os.system(cmd)
                    if result == 0:
                        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('restore.macos_platform_uuid_updated')}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.failed_to_execute_plutil_command')}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.update_macos_system_ids_failed', error=str(e))}{Style.RESET_ALL}")
    
    def restore_machine_ids(self):
        """Phuc hoi Machine ID tu backup"""
        try:
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('restore.starting')}...{Style.RESET_ALL}")
            
            # Chon backup de phuc hoi
            backup_path = self.select_backup()
            if not backup_path:
                return False
            
            # Trich xuat ID tu backup
            ids = self.extract_ids_from_backup(backup_path)
            if not ids:
                return False
            
            # Hien thi cac ID se duoc phuc hoi
            print(f"\n{Fore.CYAN}{self.translator.get('restore.ids_to_restore')}:{Style.RESET_ALL}")
            for key, value in ids.items():
                print(f"{EMOJI['INFO']} {key}: {Fore.GREEN}{value}{Style.RESET_ALL}")
            
            # Xac nhan phuc hoi
            confirm = input(f"\n{EMOJI['WARNING']} {self.translator.get('restore.confirm')} (y/n): ")
            if confirm.lower() != 'y':
                print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('restore.operation_cancelled')}{Style.RESET_ALL}")
                return False
            
            # Cap nhat file hien tai
            if not self.update_current_file(ids):
                return False
            
            # Cap nhat SQLite database
            self.update_sqlite_db(ids)
            
            # Cap nhat file machineId
            self.update_machine_id_file(ids.get("telemetry.devDeviceId", ""))
            
            # Cap nhat system ID
            self.update_system_ids(ids)
            
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('restore.success')}{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('restore.process_error', error=str(e))}{Style.RESET_ALL}")
            return False

def run(translator=None):
    """Ham chinh de phuc hoi Machine ID"""
    config = get_config(translator)
    if not config:
        return False
    
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['RESET']} {translator.get('restore.title')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    restorer = MachineIDRestorer(translator)
    restorer.restore_machine_ids()
    
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} {translator.get('restore.press_enter')}...")

if __name__ == "__main__":
    from main import translator as main_translator
    run(main_translator)   