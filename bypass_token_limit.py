# bypass_token_limit.py
import os
import shutil
import platform
import glob
import re
import time
from colorama import Fore, Style, init
import configparser
import sys
from config import get_config
from datetime import datetime

# Initialize colorama
init()

# Define emoji constants
EMOJI = {
    "FILE": "📄",
    "BACKUP": "💾",
    "SUCCESS": "✅",
    "ERROR": "❌",
    "INFO": "ℹ️",
    "RESET": "🔄",
    "WARNING": "⚠️",
}

def get_user_documents_path():
    """Get user Documents folder path"""
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders") as key:
                documents_path, _ = winreg.QueryValueEx(key, "Personal")
                return documents_path
        except Exception as e:
            return os.path.join(os.path.expanduser("~"), "Documents")
    elif sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Documents")
    else:  # Linux
        sudo_user = os.environ.get('SUDO_USER')
        if sudo_user:
            return os.path.join("/home", sudo_user, "Documents")
        return os.path.join(os.path.expanduser("~"), "Documents")

def get_workbench_cursor_path(translator=None) -> str:
    """Get Cursor workbench.desktop.main.js path"""
    system = platform.system()

    # Read configuration
    config_dir = os.path.join(get_user_documents_path(), ".cursor-pro")
    config_file = os.path.join(config_dir, "config.ini")
    config = configparser.ConfigParser()

    if os.path.exists(config_file):
        config.read(config_file)
    
    paths_map = {
        "Darwin": {  # macOS
            "base": "/Applications/Cursor.app/Contents/Resources/app",
            "main": "out/vs/workbench/workbench.desktop.main.js"
        },
        "Windows": {
            "main": "out\\vs\\workbench\\workbench.desktop.main.js"
        },
        "Linux": {
            "bases": ["/opt/Cursor/resources/app", "/usr/share/cursor/resources/app", "/usr/lib/cursor/app/"],
            "main": "out/vs/workbench/workbench.desktop.main.js"
        }
    }
    
    if system == "Linux":
        extracted_usr_paths = glob.glob(os.path.expanduser("~/squashfs-root/usr/share/cursor/resources/app"))
        paths_map["Linux"]["bases"].extend(extracted_usr_paths)

    if system not in paths_map:
        raise OSError(translator.get('reset.unsupported_os', system=system) if translator else f"He dieu hanh khong duoc ho tro: {system}")

    if system == "Linux":
        for base in paths_map["Linux"]["bases"]:
            main_path = os.path.join(base, paths_map["Linux"]["main"])
            print(f"{Fore.CYAN}{EMOJI['INFO']} Checking path: {main_path}{Style.RESET_ALL}")
            if os.path.exists(main_path):
                return main_path

    if system == "Windows":
        base_path = config.get('WindowsPaths', 'cursor_path')
    elif system == "Darwin":
        base_path = paths_map[system]["base"]
        if config.has_section('MacPaths') and config.has_option('MacPaths', 'cursor_path'):
            base_path = config.get('MacPaths', 'cursor_path')
    else:  # Linux
        base_path = paths_map[system]["bases"][0]
        if config.has_section('LinuxPaths') and config.has_option('LinuxPaths', 'cursor_path'):
            base_path = config.get('LinuxPaths', 'cursor_path')

    main_path = os.path.join(base_path, paths_map[system]["main"])
    
    if not os.path.exists(main_path):
        raise OSError(translator.get('reset.file_not_found', path=main_path) if translator else f"Khong tim thay file Cursor main.js: {main_path}")
        
    return main_path

def safe_modify_workbench_js(file_path: str, translator=None) -> bool:
    """
    Phiên bản sửa đổi an toàn - tìm kiếm thủ công từng vị trí
    """
    try:
        # Đọc file
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        modifications = []
        
        def apply_regex(pattern, replacement, description, flags: int = 0):
            nonlocal content
            new_content, count = re.subn(pattern, replacement, content, flags=flags)
            if count:
                content = new_content
                modifications.append(f"{description}: {count} matches")
        
        def replace_number_literal(value: str, new_value: str):
            nonlocal content
            pattern_context = rf'([:=,\(\[]\s*)(?:{re.escape(value)})(?=(?:\s*[,)\]\}}]))'
            count = 0
            def repl(match):
                nonlocal count
                count += 1
                return f"{match.group(1)}{new_value}"
            content_local = re.sub(pattern_context, repl, content)
            if count:
                content = content_local
                modifications.append(f"numbers ({value}): {count} contextual matches")
            # handle return statements separately
            pattern_return = rf'(return\s+)(?:{re.escape(value)})(\b)'
            count_return = 0
            def repl_return(match):
                nonlocal count_return
                count_return += 1
                return f"{match.group(1)}{new_value}"
            content_local = re.sub(pattern_return, repl_return, content)
            if count_return:
                content = content_local
                modifications.append(f"numbers ({value}): {count_return} return matches")
        
        # Ghi nhận thông tin ngữ cảnh chính (giảm để tránh log dài nhưng vẫn hỗ trợ debug)
        debug_keywords = ["getEffectiveTokenLimit", "Upgrade to Pro", "tokenLimit"]
        print(f"{Fore.CYAN}{EMOJI['INFO']} Phân tích file - sơ lược:{Style.RESET_ALL}")
        for keyword in debug_keywords:
            occurrences = content.count(keyword)
            if occurrences:
                print(f"  {keyword}: {occurrences} lần xuất hiện")
        
        # 1. Cưỡng chế trạng thái Pro
        apply_regex(r'(\bisPro\s*[:=]\s*)(?:false|!1|0)', r'\1true', "isPro override")
        apply_regex(r'(\bisProUser\s*[:=]\s*)(?:false|!1|0)', r'\1true', "isProUser override")
        
        # 2. Subscription và kế hoạch
        apply_regex(r'(\bsubscriptionType\s*[:=]\s*)(["\'])(?:free|trial)\2', r'\1\2pro\2', "subscriptionType upgrade")
        apply_regex(r'(\bplan\s*[:=]\s*)(["\'])(?:free|trial)\2', r'\1\2pro\2', "plan upgrade")
        
        # 3. Giới hạn trạng thái
        apply_regex(r'(\b(?:hasReachedLimit|isOverLimit|usageLimitReached)\s*[:=]\s*)(?:true|!0|1)', r'\1false', "limit flags")
        
        # 4. Text UI cụ thể
        apply_regex(r'(")Upgrade to Pro\+?(")', r'\1PRO Unlimited\2', "Upgrade label (double quotes)")
        apply_regex(r"(')Upgrade to Pro\+?(')", r"\1PRO Unlimited\2", "Upgrade label (single quotes)")
        apply_regex(r'\bPro Trial\b', 'Pro Unlimited', "Pro Trial text")
        
        # 5. Giá trị giới hạn token – chỉ thay literal có ngữ cảnh
        for original, new_value in {
            '200000': '999999999',
            '128000': '999999999',
            '100000': '999999999',
            '64000': '999999999',
            '32000': '999999999',
            '16000': '999999999',
            '8000': '999999999',
            '4000': '999999999',
            '30000': '900000',
            '2e5': '999999999',
        }.items():
            replace_number_literal(original, new_value)
        
        # 6. showUpgradePrompt – chỉ bổ sung return false mà không xoá phần còn lại
        apply_regex(r'(showUpgradePrompt\(\)\s*\{)', r'\1return false;', "Disable upgrade prompt")
        
        # KIỂM TRA AN TOÀN CUỐI CÙNG
        if modifications:
            print(f"\n{Fore.GREEN}{EMOJI['SUCCESS']} Đã thực hiện {len(modifications)} thay đổi:{Style.RESET_ALL}")
            for mod in modifications:
                print(f"  {Fore.GREEN}✓{Style.RESET_ALL} {mod}")
            
            # Backup và ghi file
            backup_path = f"{file_path}.backup.{int(time.time())}"
            shutil.copy2(file_path, backup_path)
            
            with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(content)
            
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã lưu thay đổi! Backup: {backup_path}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} Không có thay đổi nào được thực hiện{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi: {str(e)}{Style.RESET_ALL}")
        return False

def run(translator=None):
    config = get_config(translator)
    if not config:
        return False
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['RESET']} {translator.get('bypass_token_limit.title') if translator else '🚀 Cursor Pro Unlimited Activator'}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{EMOJI['WARNING']} ⚠️  Close Cursor completely before running this tool!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

    try:
        workbench_path = get_workbench_cursor_path(translator)
        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Found Cursor file: {workbench_path}{Style.RESET_ALL}\n")
        
        success = safe_modify_workbench_js(workbench_path, translator)
        
        if success:
            print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 🎉 SUCCESS! Cursor Pro Unlimited activated!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} ✨ All limitations removed!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 🚀 Restart Cursor to enjoy unlimited features!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.RED}{EMOJI['ERROR']} ❌ Patch failed! Please try again.{Style.RESET_ALL}")
            print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Error: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{EMOJI['WARNING']} Check Cursor path in config.ini{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} {translator.get('bypass_token_limit.press_enter') if translator else 'Press Enter to continue'}...")

if __name__ == "__main__":
    from main import translator as main_translator
    run(main_translator)