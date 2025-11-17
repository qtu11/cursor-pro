import os
import sys
import platform
import random

def get_user_documents_path():
    """Get user documents path"""
    if platform.system() == "Windows":
        try:
            import winreg
            # Mo registry
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders") as key:
                # Lay gia tri cua key "Personal", tro den thu muc Documents cua nguoi dung
                documents_path, _ = winreg.QueryValueEx(key, "Personal")
                return documents_path
        except Exception as e:
            # fallback
            return os.path.expanduser("~\\Documents")
    else:
        return os.path.expanduser("~/Documents")
    
def get_default_driver_path(browser_type='chrome'):
    """Get default driver path based on browser type"""
    browser_type = browser_type.lower()
    if browser_type == 'chrome':
        return get_default_chrome_driver_path()
    elif browser_type == 'edge':
        return get_default_edge_driver_path()
    elif browser_type == 'firefox':
        return get_default_firefox_driver_path()
    elif browser_type == 'brave':
        # Brave su dung Chrome driver
        return get_default_chrome_driver_path()
    else:
        # Default to Chrome if browser type is unknown
        return get_default_chrome_driver_path()

def get_default_chrome_driver_path():
    """Get default Chrome driver path"""
    if sys.platform == "win32":
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers", "chromedriver.exe")
    elif sys.platform == "darwin":
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers", "chromedriver")
    else:
        return "/usr/local/bin/chromedriver"

def get_default_edge_driver_path():
    """Get default Edge driver path"""
    if sys.platform == "win32":
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers", "msedgedriver.exe")
    elif sys.platform == "darwin":
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers", "msedgedriver")
    else:
        return "/usr/local/bin/msedgedriver"
        
def get_default_firefox_driver_path():
    """Get default Firefox driver path"""
    if sys.platform == "win32":
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers", "geckodriver.exe")
    elif sys.platform == "darwin":
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers", "geckodriver")
    else:
        return "/usr/local/bin/geckodriver"

def get_default_brave_driver_path():
    """Get default Brave driver path (uses Chrome driver)"""
    # Brave trinh duyet duoc xay dung tren Chromium, nen su dung cung chromedriver
    return get_default_chrome_driver_path()

def get_default_browser_path(browser_type='chrome'):
    """Get default browser executable path"""
    browser_type = browser_type.lower()
    
    if sys.platform == "win32":
        if browser_type == 'chrome':
            # Thu tim Chrome trong PATH
            try:
                import shutil
                chrome_in_path = shutil.which("chrome")
                if chrome_in_path:
                    return chrome_in_path
            except:
                pass
            # Su dung duong dan mac dinh
            return r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        elif browser_type == 'edge':
            return r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        elif browser_type == 'firefox':
            return r"C:\Program Files\Mozilla Firefox\firefox.exe"
        elif browser_type == 'opera':
            # Thu tim nhieu duong dan Opera co the
            opera_paths = [
                r"C:\Program Files\Opera\opera.exe",
                r"C:\Program Files (x86)\Opera\opera.exe",
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Opera', 'launcher.exe'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Opera', 'opera.exe')
            ]
            for path in opera_paths:
                if os.path.exists(path):
                    return path
            return opera_paths[0]  # Tra ve duong dan dau tien, ngay ca neu no khong ton tai
        elif browser_type == 'operagx':
            # Thu tim nhieu duong dan Opera GX co the
            operagx_paths = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Opera GX', 'launcher.exe'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Opera GX', 'opera.exe'),
                r"C:\Program Files\Opera GX\opera.exe",
                r"C:\Program Files (x86)\Opera GX\opera.exe"
            ]
            for path in operagx_paths:
                if os.path.exists(path):
                    return path
            return operagx_paths[0]  # Tra ve duong dan dau tien, ngay ca neu no khong ton tai
        elif browser_type == 'brave':
            # Duong dan cai dat mac dinh cua Brave trinh duyet
            paths = [
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'BraveSoftware/Brave-Browser/Application/brave.exe'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'BraveSoftware/Brave-Browser/Application/brave.exe'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'BraveSoftware/Brave-Browser/Application/brave.exe')
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
            return paths[0]  # Tra ve duong dan dau tien, ngay ca neu no khong ton tai
    
    elif sys.platform == "darwin":
        if browser_type == 'chrome':
            return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        elif browser_type == 'edge':
            return "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        elif browser_type == 'firefox':
            return "/Applications/Firefox.app/Contents/MacOS/firefox"
        elif browser_type == 'brave':
            return "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        elif browser_type == 'opera':
            return "/Applications/Opera.app/Contents/MacOS/Opera"
        elif browser_type == 'operagx':
            return "/Applications/Opera GX.app/Contents/MacOS/Opera"
        
    else:  # Linux
        if browser_type == 'chrome':
            # Thu tim nhieu ten co the
            chrome_names = ["google-chrome", "chrome", "chromium", "chromium-browser"]
            for name in chrome_names:
                try:
                    import shutil
                    path = shutil.which(name)
                    if path:
                        return path
                except:
                    pass
            return "/usr/bin/google-chrome"
        elif browser_type == 'edge':
            return "/usr/bin/microsoft-edge"
        elif browser_type == 'firefox':
            return "/usr/bin/firefox"
        elif browser_type == 'opera':
            return "/usr/bin/opera"
        elif browser_type == 'operagx':
            # Thu tim cac duong dan Opera GX pho bien
            operagx_names = ["opera-gx"]
            for name in operagx_names:
                try:
                    import shutil
                    path = shutil.which(name)
                    if path:
                        return path
                except:
                    pass
            return "/usr/bin/opera-gx"
        elif browser_type == 'brave':
            # Thu tim cac duong dan Brave pho bien
            brave_names = ["brave", "brave-browser"]
            for name in brave_names:
                try:
                    import shutil
                    path = shutil.which(name)
                    if path:
                        return path
                except:
                    pass
            return "/usr/bin/brave-browser"
    
    # Neu khong tim thay loai trinh duyet chi dinh, tra ve duong dan Chrome
    return get_default_browser_path('chrome')

def get_linux_cursor_path():
    """Get Linux Cursor path"""
    possible_paths = [
        "/opt/Cursor/resources/app",
        "/usr/share/cursor/resources/app",
        "/opt/cursor-bin/resources/app",
        "/usr/lib/cursor/resources/app",
        os.path.expanduser("~/.local/share/cursor/resources/app")
    ]
    
    # return the first path that exists
    return next((path for path in possible_paths if os.path.exists(path)), possible_paths[0])

def get_random_wait_time(config, timing_key):
    """Get random wait time based on configuration timing settings
    
    Args:
        config (dict): Configuration dictionary containing timing settings
        timing_key (str): Key to look up in the timing settings
        
    Returns:
        float: Random wait time in seconds
    """
    try:
        # Get timing value from config
        timing = config.get('Timing', {}).get(timing_key)
        if not timing:
            # Default to 0.5-1.5 seconds if timing not found
            return random.uniform(0.5, 1.5)
            
        # Check if timing is a range (e.g., "0.5-1.5" or "0.5,1.5")
        if isinstance(timing, str):
            if '-' in timing:
                min_time, max_time = map(float, timing.split('-'))
            elif ',' in timing:
                min_time, max_time = map(float, timing.split(','))
            else:
                # Single value, use it as both min and max
                min_time = max_time = float(timing)
        else:
            # If timing is a number, use it as both min and max
            min_time = max_time = float(timing)
            
        return random.uniform(min_time, max_time)
        
    except (ValueError, TypeError, AttributeError):
        # Return default value if any error occurs
        return random.uniform(0.5, 1.5) 