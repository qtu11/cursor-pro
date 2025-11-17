# bypass_version.py
import os
import json
import shutil
import platform
import configparser
import time
from colorama import Fore, Style, init
import sys
import traceback
from utils import get_user_documents_path

# Initialize colorama
init()

# Define emoji constants
EMOJI = {
    'INFO': 'ℹ️',
    'SUCCESS': '✅',
    'ERROR': '❌',
    'WARNING': '⚠️',
    'FILE': '📄',
    'BACKUP': '💾',
    'RESET': '🔄',
    'VERSION': '🏷️'
}

def get_product_json_path(translator=None):
    """Get Cursor product.json path with enhanced detection"""
    system = platform.system()
    
    # Read configuration
    config_dir = os.path.join(get_user_documents_path(), ".cursor-pro")
    config_file = os.path.join(config_dir, "config.ini")
    config = configparser.ConfigParser()
    
    if os.path.exists(config_file):
        config.read(config_file)
    
    possible_paths = []
    
    if system == "Windows":
        # Multiple Windows paths
        windows_paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Cursor", "resources", "app", "product.json"),
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Cursor", "resources", "app", "product.json"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Cursor", "resources", "app", "product.json"),
        ]
        possible_paths.extend(windows_paths)
        
        # Check config path
        if 'WindowsPaths' in config and 'cursor_path' in config['WindowsPaths']:
            cursor_path = config.get('WindowsPaths', 'cursor_path')
            possible_paths.append(os.path.join(cursor_path, "product.json"))
    
    elif system == "Darwin":  # macOS
        mac_paths = [
            "/Applications/Cursor.app/Contents/Resources/app/product.json",
            os.path.expanduser("~/Applications/Cursor.app/Contents/Resources/app/product.json"),
        ]
        possible_paths.extend(mac_paths)
        
        if config.has_section('MacPaths') and config.has_option('MacPaths', 'product_json_path'):
            possible_paths.append(config.get('MacPaths', 'product_json_path'))
    
    elif system == "Linux":
        linux_paths = [
            "/opt/Cursor/resources/app/product.json",
            "/usr/share/cursor/resources/app/product.json",
            "/usr/lib/cursor/app/product.json",
            os.path.expanduser("~/.cursor/resources/app/product.json"),
            os.path.expanduser("~/cursor/resources/app/product.json"),
        ]
        possible_paths.extend(linux_paths)
        
        # Add extracted AppImage paths
        extracted_paths = [
            os.path.expanduser("~/squashfs-root/usr/share/cursor/resources/app/product.json"),
            os.path.expanduser("~/squashfs-root/opt/cursor/resources/app/product.json"),
        ]
        possible_paths.extend(extracted_paths)
    
    else:
        raise OSError(translator.get('bypass.unsupported_os', system=system) if translator else f"Unsupported operating system: {system}")
    
    # Find existing path
    for path in possible_paths:
        if os.path.exists(path):
            print(f"{Fore.CYAN}{EMOJI['INFO']} Found product.json at: {path}{Style.RESET_ALL}")
            return path
    
    # If no path found, try to detect Cursor installation
    cursor_path = detect_cursor_installation(system)
    if cursor_path:
        product_path = os.path.join(cursor_path, "resources", "app", "product.json")
        if os.path.exists(product_path):
            return product_path
    
    raise OSError(translator.get('bypass.product_json_not_found') if translator else "product.json not found in common paths")

def detect_cursor_installation(system):
    """Detect Cursor installation location"""
    if system == "Windows":
        # Check common installation directories
        possible_dirs = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Cursor"),
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Cursor"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Cursor"),
        ]
        for dir_path in possible_dirs:
            if os.path.exists(dir_path):
                return dir_path
    elif system == "Darwin":
        if os.path.exists("/Applications/Cursor.app"):
            return "/Applications/Cursor.app/Contents"
    elif system == "Linux":
        linux_dirs = [
            "/opt/Cursor",
            "/usr/share/cursor",
            "/usr/lib/cursor",
            os.path.expanduser("~/.cursor"),
        ]
        for dir_path in linux_dirs:
            if os.path.exists(dir_path):
                return dir_path
    return None

def compare_versions(version1, version2):
    """Compare two version strings"""
    def parse_version(version):
        parts = []
        for part in version.split('.'):
            try:
                parts.append(int(part))
            except ValueError:
                # Handle non-numeric parts (like beta, rc, etc.)
                parts.append(0)
        return parts
    
    v1_parts = parse_version(version1)
    v2_parts = parse_version(version2)
    
    for i in range(max(len(v1_parts), len(v2_parts))):
        v1 = v1_parts[i] if i < len(v1_parts) else 0
        v2 = v2_parts[i] if i < len(v2_parts) else 0
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
    
    return 0

def bypass_version(translator=None):
    """Enhanced Cursor version bypass with comprehensive modifications"""
    try:
        print(f"\n{Fore.CYAN}{EMOJI['INFO']} {translator.get('bypass.starting') if translator else '🚀 Starting Cursor Version Bypass...'}{Style.RESET_ALL}")
        
        # Get product.json path
        product_json_path = get_product_json_path(translator)
        print(f"{Fore.CYAN}{EMOJI['FILE']} {translator.get('bypass.found_product_json', path=product_json_path) if translator else f'📁 Found product.json: {product_json_path}'}{Style.RESET_ALL}")
        
        # Check file permissions
        if not os.access(product_json_path, os.W_OK):
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('bypass.no_write_permission', path=product_json_path) if translator else f'❌ No write permission for file: {product_json_path}'}{Style.RESET_ALL}")
            
            # Try to gain permissions on Linux/macOS
            if system != "Windows":  # pyright: ignore[reportUndefinedVariable]
                try:
                    import subprocess
                    subprocess.run(['sudo', 'chmod', '666', product_json_path], check=True)
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Fixed permissions for product.json{Style.RESET_ALL}")
                except:
                    pass
        
        # Read product.json
        try:
            with open(product_json_path, "r", encoding="utf-8") as f:
                product_data = json.load(f)
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('bypass.read_failed', error=str(e)) if translator else f'❌ Failed to read product.json: {str(e)}'}{Style.RESET_ALL}")
            return False
        
        # Get current version
        current_version = product_data.get("version", "0.0.0")
        print(f"{Fore.CYAN}{EMOJI['VERSION']} {translator.get('bypass.current_version', version=current_version) if translator else f'🏷️ Current version: {current_version}'}{Style.RESET_ALL}")
        
        # Create backup
        timestamp = time.strftime("%Y%m%d%H%M%S")
        backup_path = f"{product_json_path}.backup.{timestamp}"
        shutil.copy2(product_json_path, backup_path)
        print(f"{Fore.GREEN}{EMOJI['BACKUP']} {translator.get('bypass.backup_created', path=backup_path) if translator else f'💾 Backup created: {backup_path}'}{Style.RESET_ALL}")
        
        # Enhanced version modifications
        modifications_made = 0
        
        # 1. Update version to latest stable
        new_version = "0.48.7"
        if product_data.get("version") != new_version:
            product_data["version"] = new_version
            modifications_made += 1
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('bypass.version_updated', old=current_version, new=new_version) if translator else f'✅ Version updated from {current_version} to {new_version}'}{Style.RESET_ALL}")
        
        # 2. Remove update checks
        if "updateUrl" in product_data:
            product_data["updateUrl"] = ""
            modifications_made += 1
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} ✅ Update checks disabled{Style.RESET_ALL}")
        
        # 3. Modify quality to 'stable'
        if product_data.get("quality") != "stable":
            product_data["quality"] = "stable"
            modifications_made += 1
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} ✅ Quality set to stable{Style.RESET_ALL}")
        
        # 4. Remove telemetry
        if "telemetry" in product_data:
            product_data["telemetry"] = {}
            modifications_made += 1
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} ✅ Telemetry disabled{Style.RESET_ALL}")
        
        # 5. Add extension recommendations bypass
        if "extensionAllowedProposedApi" not in product_data:
            product_data["extensionAllowedProposedApi"] = ["*"]
            modifications_made += 1
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} ✅ Extension restrictions removed{Style.RESET_ALL}")
        
        # 6. Enable all features
        feature_flags = {
            "enableProposedApi": True,
            "enablePreviewFeatures": True,
            "enableExperimentalFeatures": True,
            "disableHardwareAcceleration": False,
        }
        
        for flag, value in feature_flags.items():
            if product_data.get(flag) != value:
                product_data[flag] = value
                modifications_made += 1
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} ✅ {flag} enabled{Style.RESET_ALL}")
        
        # Save modified product.json
        try:
            with open(product_json_path, "w", encoding="utf-8") as f:
                json.dump(product_data, f, indent=2, ensure_ascii=False)
            
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('bypass.write_success') if translator else '✅ product.json successfully modified!'}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{EMOJI['INFO']} Total modifications: {modifications_made}{Style.RESET_ALL}")
            
            if modifications_made > 0:
                print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 🎉 VERSION BYPASS COMPLETE!{Style.RESET_ALL}")
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} ✨ Cursor will now ignore version checks!{Style.RESET_ALL}")
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 🚀 All features unlocked!{Style.RESET_ALL}")
                print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('bypass.write_failed', error=str(e)) if translator else f'❌ Failed to write product.json: {str(e)}'}{Style.RESET_ALL}")
            return False
    
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('bypass.bypass_failed', error=str(e)) if translator else f'❌ Version bypass failed: {str(e)}'}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('bypass.stack_trace') if translator else 'Stack trace'}: {traceback.format_exc()}{Style.RESET_ALL}")
        return False

def main(translator=None):
    """Main function"""
    return bypass_version(translator)

if __name__ == "__main__":
    main()