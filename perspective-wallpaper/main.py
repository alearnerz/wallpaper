import os
import sys
import json
import platform
import webbrowser
from pathlib import Path


def get_resource_path(relative_path: str = "") -> str:
    if getattr(sys, '_MEIPASS', None):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def get_config_path() -> str:
    if getattr(sys, '_MEIPASS', None):
        exe_dir = os.path.dirname(sys.executable)
        config_path = os.path.join(exe_dir, 'config.json')
        if os.path.exists(config_path):
            return config_path
    return get_resource_path('config.json')


def load_config() -> dict:
    default_config = {
        "spotSize": 0.15,
        "blendStrength": 0.95,
        "edgeSoftness": 0.3,
        "foregroundImage": "assets/base.png",
        "backgroundImage": "assets/xray.png"
    }
    try:
        config_path = get_config_path()
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                default_config.update(loaded)
    except Exception:
        pass
    return default_config


def save_config(config_json: str) -> bool:
    try:
        if getattr(sys, '_MEIPASS', None):
            exe_dir = os.path.dirname(sys.executable)
            config_path = os.path.join(exe_dir, 'config.json')
        else:
            config_path = get_resource_path('config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_json)
        return True
    except Exception:
        return False


class WallpaperAPI:
    def save_config(self, config_json: str) -> bool:
        return save_config(config_json)


def find_workerw_window():
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32

        WorkerW = None
        Progman = user32.FindWindowW('Progman', None)

        result = wintypes.DWORD()
        user32.SendMessageTimeoutW(
            Progman, 0x052C,
            wintypes.WPARAM(0),
            wintypes.LPARAM(0),
            wintypes.UINT(2),
            wintypes.UINT(1000),
            ctypes.byref(result)
        )

        def enum_windows_proc(hwnd, lParam):
            nonlocal WorkerW
            shell_view = user32.FindWindowExW(hwnd, 0, 'SHELLDLL_DefView', None)
            if shell_view:
                WorkerW = user32.FindWindowExW(0, hwnd, 'WorkerW', None)
            return True

        EnumWindowsProc = ctypes.WINFUNCTYPE(
            wintypes.BOOL, wintypes.HWND, wintypes.LPARAM
        )
        proc = EnumWindowsProc(enum_windows_proc)
        user32.EnumWindows(proc, 0)

        return WorkerW
    except Exception:
        return None


def embed_to_desktop(hwnd_target):
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        workerw = find_workerw_window()
        if workerw:
            user32.SetParent(hwnd_target, workerw)
            return True
    except Exception:
        pass
    return False


def is_windows() -> bool:
    return platform.system() == 'Windows'


def main():
    config = load_config()
    api = WallpaperAPI()

    index_path = os.path.abspath(get_resource_path('index.html'))
    index_url = 'file://' + index_path.replace('\\', '/')

    try:
        import webview
    except ImportError:
        print("正在打开浏览器预览模式...")
        webbrowser.open(index_url)
        input("按回车键退出...")
        return

    screen_width = 1920
    screen_height = 1080
    try:
        import tkinter as tk
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
    except Exception:
        pass

    window = webview.create_window(
        title='透视壁纸',
        url=index_url,
        x=0,
        y=0,
        width=screen_width,
        height=screen_height,
        resizable=False,
        fullscreen=False,
        frameless=True,
        easy_drag=False,
        on_top=False,
        confirm_close=False,
        background_color='#000000',
        js_api=api
    )

    def on_loaded():
        if is_windows():
            try:
                hwnd = window.native_identifier()
                if hwnd:
                    embed_to_desktop(hwnd)
            except Exception:
                pass

    try:
        webview.start(
            func=on_loaded,
            debug=False,
            gui='edgechromium' if is_windows() else None
        )
    except Exception as e:
        print(f"启动失败: {e}")
        print("正在打开浏览器预览模式...")
        webbrowser.open(index_url)


if __name__ == '__main__':
    main()
