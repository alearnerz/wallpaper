import os
import sys
import json
import platform
import webbrowser
import urllib.parse
from pathlib import Path


def get_resource_path(relative_path: str = "") -> str:
    if getattr(sys, '_MEIPASS', None):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def get_app_dir() -> str:
    if getattr(sys, '_MEIPASS', None):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_config_path() -> str:
    app_dir = get_app_dir()
    config_path = os.path.join(app_dir, 'config.json')
    if os.path.exists(config_path):
        return config_path
    return get_resource_path('config.json')


def resolve_image_path(image_path: str) -> str:
    if os.path.isabs(image_path):
        return image_path
    app_dir = get_app_dir()
    candidate = os.path.join(app_dir, image_path)
    if os.path.exists(candidate):
        return candidate
    return get_resource_path(image_path)


def detect_image_format(base_path_no_ext: str) -> str:
    for ext in ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif']:
        candidate = base_path_no_ext + ext
        if os.path.exists(candidate):
            return candidate
    return base_path_no_ext + '.png'


def path_to_file_url(path: str) -> str:
    abs_path = os.path.abspath(path)
    path_normalized = abs_path.replace('\\', '/')
    if path_normalized.startswith('/'):
        return 'file://' + urllib.parse.quote(path_normalized, safe='/:')
    else:
        return 'file:///' + urllib.parse.quote(path_normalized, safe='/:')


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

    fg_path = resolve_image_path(default_config["foregroundImage"])
    bg_path = resolve_image_path(default_config["backgroundImage"])

    fg_base = os.path.splitext(fg_path)[0]
    bg_base = os.path.splitext(bg_path)[0]

    fg_path = detect_image_format(fg_base)
    bg_path = detect_image_format(bg_base)

    default_config["foregroundImage"] = path_to_file_url(fg_path)
    default_config["backgroundImage"] = path_to_file_url(bg_path)

    return default_config


def save_config(config_json: str) -> bool:
    try:
        app_dir = get_app_dir()
        config_path = os.path.join(app_dir, 'config.json')
        try:
            config = json.loads(config_json)
            save_config_data = {
                "spotSize": config.get("spotSize", 0.15),
                "blendStrength": config.get("blendStrength", 0.95),
                "edgeSoftness": config.get("edgeSoftness", 0.3),
                "foregroundImage": "assets/base.png",
                "backgroundImage": "assets/xray.png"
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(save_config_data, f, indent=2, ensure_ascii=False)
        except Exception:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_json)
        return True
    except Exception:
        return False


class WallpaperAPI:
    def save_config(self, config_json: str) -> bool:
        return save_config(config_json)

    def get_config(self) -> str:
        config = load_config()
        return json.dumps(config, ensure_ascii=False)


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

    index_path = get_resource_path('index.html')
    index_url = path_to_file_url(index_path)

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
