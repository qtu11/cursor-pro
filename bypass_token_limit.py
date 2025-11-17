import os
import shutil
import platform
import tempfile
import glob
import re
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
             # fallback
             return os.path.join(os.path.expanduser("~"), "Documents")
     elif sys.platform == "darwin":
         return os.path.join(os.path.expanduser("~"), "Documents")
     else:  # Linux
         # Get actual user's home directory
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
        # Add extracted AppImage with correct usr structure
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
        # For Linux, we've already checked all bases in the loop above
        # If we're here, it means none of the bases worked, so we'll use the first one
        base_path = paths_map[system]["bases"][0]
        if config.has_section('LinuxPaths') and config.has_option('LinuxPaths', 'cursor_path'):
            base_path = config.get('LinuxPaths', 'cursor_path')

    main_path = os.path.join(base_path, paths_map[system]["main"])
    
    if not os.path.exists(main_path):
        raise OSError(translator.get('reset.file_not_found', path=main_path) if translator else f"Khong tim thay file Cursor main.js: {main_path}")
        
    return main_path


def modify_workbench_js(file_path: str, translator=None) -> bool:
    """
    Modify file content
    """
    try:
        # Save original file permissions
        original_stat = os.stat(file_path)
        original_mode = original_stat.st_mode
        original_uid = original_stat.st_uid
        original_gid = original_stat.st_gid

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", errors="ignore", delete=False) as tmp_file:
            # Read original content
            with open(file_path, "r", encoding="utf-8", errors="ignore") as main_file:
                content = main_file.read()

            # Counter để đếm số pattern đã match
            matches_count = 0
            
            # ===== PATTERN 1: UPGRADE TO PRO BUTTONS =====
            # Thay thế tất cả các nút "Upgrade to Pro" bằng GitHub link
            upgrade_patterns = [
                # Pattern cơ bản
                (r'B\(k,D\(Ln,\{title:"Upgrade to Pro"[^}]*\}\),null\)', 
                 r'B(k,D(Ln,{title:"qtusdev GitHub",size:"small",get codicon(){return A.github},get onClick(){return function(){window.open("https://github.com/qtu11/cursor-pro","_blank")}}}),null)'),
                
                (r'M\(x,I\(as,\{title:"Upgrade to Pro"[^}]*\}\),null\)',
                 r'M(x,I(as,{title:"qtusdev GitHub",size:"small",get codicon(){return $.github},get onClick(){return function(){window.open("https://github.com/qtu11/cursor-pro","_blank")}}}),null)'),
                
                (r'\$\(k,E\(Ks,\{title:"Upgrade to Pro"[^}]*\}\),null\)',
                 r'$(k,E(Ks,{title:"qtusdev GitHub",size:"small",get codicon(){return F.github},get onClick(){return function(){window.open("https://github.com/qtu11/cursor-pro","_blank")}}}),null)'),
                
                # Pattern tổng quát hơn - bất kỳ "Upgrade to Pro" nào
                (r'title:"Upgrade to Pro"', r'title:"qtusdev GitHub"'),
                (r'"Upgrade to Pro"', r'"qtusdev GitHub"'),
                (r'Upgrade to Pro', r'qtusdev GitHub'),
            ]
            
            for pattern, replacement in upgrade_patterns:
                new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                if new_content != content:
                    matches_count += 1
                    content = new_content
            
            # ===== PATTERN 2: TOKEN LIMIT BYPASS =====
            # Bypass hoàn toàn token limit - đặt giá trị rất lớn
            token_limit_patterns = [
                # Pattern chính
                (r'async getEffectiveTokenLimit\(e\)\{const n=e\.modelName;if\(!n\)return 2e5;',
                 r'async getEffectiveTokenLimit(e){return 999999999;const n=e.modelName;if(!n)return 999999999;'),
                
                # Các biến thể khác
                (r'getEffectiveTokenLimit.*return.*2e5', r'getEffectiveTokenLimit(){return 999999999'),
                (r'getEffectiveTokenLimit.*return.*200000', r'getEffectiveTokenLimit(){return 999999999'),
                (r'tokenLimit.*200000', r'tokenLimit:999999999'),
                (r'tokenLimit.*2e5', r'tokenLimit:999999999'),
                (r'return 2e5', r'return 999999999'),
                (r'return 200000', r'return 999999999'),
                
                # Token limit trong các function khác
                (r'\.tokenLimit\s*=\s*\d+', r'.tokenLimit = 999999999'),
                (r'tokenLimit:\s*\d+', r'tokenLimit:999999999'),
            ]
            
            for pattern, replacement in token_limit_patterns:
                new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                if new_content != content:
                    matches_count += 1
                    content = new_content
            
            # ===== PATTERN 3: HIDE CONTEXT USED PERCENTAGE =====
            # Ẩn phần trăm context used
            context_used_patterns = [
                # Ẩn text "context used" và phần trăm
                (r'\d+\.?\d*%\s*context\s*used', r''),
                (r'context\s*used\s*\d+\.?\d*%', r''),
                (r'contextUsed.*%', r''),
                (r'%.*context.*used', r''),
                (r'context.*usage.*%', r''),
                
                # Ẩn trong template strings
                (r'`[^`]*\$\{[^}]*context[^}]*used[^}]*\}[^`]*`', r'``'),
                (r'`[^`]*\$\{[^}]*percentage[^}]*\}[^`]*`', r'``'),
                
                # Ẩn trong JSX/HTML
                (r'<[^>]*>.*?context.*?used.*?</[^>]*>', r'<div style="display:none"></div>'),
                (r'<[^>]*>.*?\d+\.?\d*%.*?context.*?</[^>]*>', r'<div style="display:none"></div>'),
                
                # Ẩn class chứa context used
                (r'class="[^"]*context[^"]*used[^"]*"', r'class="hidden"'),
                (r'className="[^"]*context[^"]*used[^"]*"', r'className="hidden"'),
                
                # Ẩn trong React components
                (r'\{[^}]*context[^}]*used[^}]*\}', r'{}'),
                (r'\{[^}]*\d+\.?\d*%[^}]*context[^}]*\}', r'{}'),
            ]
            
            for pattern, replacement in context_used_patterns:
                try:
                    new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE | re.DOTALL)
                    if new_content != content:
                        matches_count += 1
                        content = new_content
                except:
                    pass
            
            # ===== PATTERN 4: PRO TRIAL BADGE =====
            # Thay Pro Trial thành Pro
            pro_patterns = [
                (r'<div>Pro Trial', r'<div>Pro'),
                (r'Pro Trial', r'Pro'),
                (r'"Pro Trial"', r'"Pro"'),
            ]
            
            for pattern, replacement in pro_patterns:
                new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                if new_content != content:
                    matches_count += 1
                    content = new_content
            
            # ===== PATTERN 5: PRO STATUS =====
            # Đảm bảo hiển thị Pro status
            pro_status_patterns = [
                (r'var DWr=ne\("<div class=settings__item_description>You are currently signed in with <strong></strong>\."\);',
                 r'var DWr=ne("<div class=settings__item_description>You are currently signed in with <strong></strong>. <h1>Pro</h1>");'),
            ]
            
            for pattern, replacement in pro_status_patterns:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    matches_count += 1
                    content = new_content
            
            # ===== PATTERN 6: HIDE NOTIFICATIONS =====
            # Ẩn notifications
            notification_patterns = [
                (r'notifications-toasts', r'notifications-toasts hidden'),
                (r'upgradePro', r'hidden'),
                (r'upgrade.*pro', r'hidden'),
                (r'upgrade.*notification', r'hidden'),
            ]
            
            for pattern, replacement in notification_patterns:
                new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                if new_content != content:
                    matches_count += 1
                    content = new_content
            
            # ===== PATTERN 7: AUTO-SELECT =====
            # Thay Auto-select
            if 'py-1">Auto-select' in content:
                content = content.replace('py-1">Auto-select', 'py-1">Bypass-Version-Pin')
                matches_count += 1
            
            # ===== PATTERN 8: ADDITIONAL BYPASSES =====
            # Bypass các check khác liên quan đến limits
            additional_bypasses = [
                # Bypass usage limits
                (r'usageLimit.*\d+', r'usageLimit:999999999'),
                (r'usage.*limit.*\d+', r'usageLimit:999999999'),
                (r'isOverLimit', r'false'),
                (r'isOverTokenLimit', r'false'),
                (r'hasReachedLimit', r'false'),
                
                # Bypass subscription checks
                (r'isPro.*false', r'isPro:true'),
                (r'isPro\s*=\s*false', r'isPro=true'),
                (r'subscription.*trial', r'subscription:"pro"'),
                
                # Hide upgrade prompts
                (r'showUpgradePrompt', r'false'),
                (r'showUpgrade.*true', r'showUpgrade:false'),
            ]
            
            for pattern, replacement in additional_bypasses:
                try:
                    new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                    if new_content != content:
                        matches_count += 1
                        content = new_content
                except:
                    pass
            
            # ===== PATTERN 9: BYPASS CLAUDE LIMIT =====
            # Bypass Claude token limit (30000 -> 900000)
            claude_limit_patterns = [
                (r'Claude.*30000', r'Claude:900000'),
                (r'claude.*30000', r'claude:900000'),
                (r'30000.*claude', r'900000'),
                (r'limit.*30000', r'limit:900000'),
            ]
            
            for pattern, replacement in claude_limit_patterns:
                try:
                    new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                    if new_content != content:
                        matches_count += 1
                        content = new_content
                except:
                    pass
            
            # ===== PATTERN 10: HIDE CONTEXT USAGE UI ELEMENTS =====
            # Ẩn các UI element hiển thị context usage
            ui_hide_patterns = [
                # Ẩn progress bars
                (r'progress.*context', r'style="display:none"'),
                (r'context.*progress', r'style="display:none"'),
                
                # Ẩn tooltips
                (r'tooltip.*context.*used', r''),
                (r'context.*used.*tooltip', r''),
                
                # Ẩn badges
                (r'badge.*context', r'style="display:none"'),
                (r'context.*badge', r'style="display:none"'),
            ]
            
            for pattern, replacement in ui_hide_patterns:
                try:
                    new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                    if new_content != content:
                        matches_count += 1
                        content = new_content
                except:
                    pass
            
            # ===== PATTERN 11: FORCE PRO MODE =====
            # Force enable Pro mode trong các check
            force_pro_patterns = [
                (r'\.isPro\s*=\s*false', r'.isPro=true'),
                (r'isPro:\s*false', r'isPro:true'),
                (r'plan.*free', r'plan:"pro"'),
                (r'plan.*trial', r'plan:"pro"'),
                (r'subscriptionType.*free', r'subscriptionType:"pro"'),
                (r'subscriptionType.*trial', r'subscriptionType:"pro"'),
            ]
            
            for pattern, replacement in force_pro_patterns:
                try:
                    new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                    if new_content != content:
                        matches_count += 1
                        content = new_content
                except:
                    pass

            # Write to temporary file
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Backup original file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup.{timestamp}"
        shutil.copy2(file_path, backup_path)
        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('reset.backup_created', path=backup_path)}{Style.RESET_ALL}")
        
        # Move temporary file to original position
        if os.path.exists(file_path):
            os.remove(file_path)
        shutil.move(tmp_path, file_path)

        # Restore original permissions
        os.chmod(file_path, original_mode)
        if os.name != "nt":  # Not Windows
            os.chown(file_path, original_uid, original_gid)

        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('reset.file_modified') if translator else 'File modified successfully'}{Style.RESET_ALL}")
        
        # Hiển thị thống kê
        if 'matches_count' in locals() and matches_count > 0:
            print(f"{Fore.CYAN}{EMOJI['INFO']} Đã áp dụng {matches_count} pattern replacements{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Token limit đã được bypass thành công!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Thông báo 'Upgrade to Pro' đã được ẩn!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Phần trăm 'context used' đã được ẩn!{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} Không tìm thấy pattern nào để thay thế. Có thể file đã được patch trước đó hoặc phiên bản Cursor khác.{Style.RESET_ALL}")
        
        return True

    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('reset.modify_file_failed', error=str(e))}{Style.RESET_ALL}")
        if "tmp_path" in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        return False
    
def run(translator=None):
    config = get_config(translator)
    if not config:
        return False
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['RESET']} {translator.get('bypass_token_limit.title') if translator else 'Bypass Token Limit Tool'}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{EMOJI['WARNING']} Lưu ý: Vui lòng đóng Cursor trước khi chạy tool này!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

    try:
        workbench_path = get_workbench_cursor_path(translator)
        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã tìm thấy file: {workbench_path}{Style.RESET_ALL}\n")
        
        success = modify_workbench_js(workbench_path, translator)
        
        if success:
            print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Hoàn tất! Bây giờ bạn có thể mở lại Cursor.{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Cursor sẽ không còn giới hạn token và không hiển thị thông báo upgrade.{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.RED}{EMOJI['ERROR']} Có lỗi xảy ra trong quá trình patch!{Style.RESET_ALL}")
            print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{EMOJI['WARNING']} Vui lòng kiểm tra đường dẫn Cursor trong config.ini{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} {translator.get('bypass_token_limit.press_enter') if translator else 'Nhấn Enter để tiếp tục'}...")

if __name__ == "__main__":
    from main import translator as main_translator
    run(main_translator)