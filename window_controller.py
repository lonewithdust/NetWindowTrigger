import os
import sys
import time
import subprocess
import webbrowser
from flask import Flask, request, jsonify

try:
    import pygetwindow as gw
    import win32gui
    import win32con
    import win32process
except ImportError:
    print("请先安装依赖: pip install -r requirements.txt")
    sys.exit(1)

app = Flask(__name__)

def find_window_by_title(title):
    """根据标题查找窗口"""
    try:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            return windows[0]
        return None
    except Exception as e:
        print(f"查找窗口失败: {e}")
        return None

def maximize_window(window_title):
    """最大化指定窗口"""
    window = find_window_by_title(window_title)
    if window:
        try:
            window.maximize()
            return True, f"窗口 '{window_title}' 已最大化"
        except Exception as e:
            return False, f"最大化窗口失败: {e}"
    return False, f"未找到窗口: {window_title}"

def minimize_window(window_title):
    """最小化指定窗口"""
    window = find_window_by_title(window_title)
    if window:
        try:
            window.minimize()
            return True, f"窗口 '{window_title}' 已最小化"
        except Exception as e:
            return False, f"最小化窗口失败: {e}"
    return False, f"未找到窗口: {window_title}"

def activate_window(window_title):
    """激活指定窗口"""
    window = find_window_by_title(window_title)
    if window:
        try:
            window.activate()
            return True, f"窗口 '{window_title}' 已激活"
        except Exception as e:
            return False, f"激活窗口失败: {e}"
    return False, f"未找到窗口: {window_title}"

def get_window_hwnd(window_title):
    """根据窗口标题获取窗口句柄"""
    # 方法1：通过pygetwindow获取
    window = find_window_by_title(window_title)
    if window:
        try:
            # pygetwindow的Win32Window对象使用_hWnd属性
            return window._hWnd
        except AttributeError:
            pass
    
    # 方法2：通过win32gui直接查找
    try:
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            return hwnd
    except Exception:
        pass
    
    # 方法3：遍历所有窗口查找匹配的
    def enum_windows_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if window_title.lower() in title.lower():
                results.append(hwnd)
        return True
    
    results = []
    win32gui.EnumWindows(enum_windows_callback, results)
    if results:
        return results[0]
    
    return None

def set_window_topmost(window_title):
    """将指定窗口置顶（最上层显示）"""
    hwnd = get_window_hwnd(window_title)
    if hwnd:
        try:
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                                   win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
            return True, f"窗口 '{window_title}' 已置顶"
        except Exception as e:
            return False, f"置顶窗口失败: {e}"
    return False, f"未找到窗口: {window_title}"

def activate_maximize_topmost(window_title):
    """激活、最大化并将窗口放到最上层（不置顶）"""
    hwnd = get_window_hwnd(window_title)
    if hwnd:
        try:
            # 1. 先恢复窗口到正常状态
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # 2. 最大化窗口
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            
            # 3. 将窗口放到最上层
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0,
                                   win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
            
            # 4. 尝试激活窗口到前台（绕过Windows限制）
            try:
                # 方法1：模拟按键来绕过SetForegroundWindow限制
                import ctypes
                # 允许进程调用SetForegroundWindow
                ctypes.windll.user32.AllowSetForegroundWindow(win32process.GetWindowThreadProcessId(hwnd)[0])
                win32gui.SetForegroundWindow(hwnd)
            except Exception:
                # 方法2：如果失败，使用BringWindowToTop
                try:
                    win32gui.BringWindowToTop(hwnd)
                except Exception:
                    pass
            
            return True, f"窗口 '{window_title}' 已激活、最大化并放到最上层"
        except Exception as e:
            return False, f"操作窗口失败: {e}"
    return False, f"未找到窗口: {window_title}"

def remove_window_topmost(window_title):
    """取消窗口置顶"""
    hwnd = get_window_hwnd(window_title)
    if hwnd:
        try:
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                   win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
            return True, f"窗口 '{window_title}' 已取消置顶"
        except Exception as e:
            return False, f"取消置顶失败: {e}"
    return False, f"未找到窗口: {window_title}"

def open_url(url):
    """打开网页并最大化浏览器窗口"""
    try:
        webbrowser.open(url)
        time.sleep(2)
        browsers = ["Google Chrome", "Microsoft Edge", "Firefox", "Opera"]
        for browser in browsers:
            window = find_window_by_title(browser)
            if window:
                # 激活、最大化并置顶浏览器窗口
                success, msg = activate_maximize_topmost(browser)
                return True, f"已打开网页: {url}，{msg}"
        return True, f"已打开网页: {url}，但未找到浏览器窗口"
    except Exception as e:
        return False, f"打开网页失败: {e}"

def start_exe(exe_path):
    """启动exe应用并最大化窗口"""
    if not os.path.exists(exe_path):
        return False, f"文件不存在: {exe_path}"
    
    try:
        subprocess.Popen(exe_path)
        time.sleep(3)
        
        exe_name = os.path.basename(exe_path).replace('.exe', '')
        # 激活、最大化并置顶窗口
        success, msg = activate_maximize_topmost(exe_name)
        if success:
            return True, f"已启动应用: {exe_path}，{msg}"
        
        return True, f"已启动应用: {exe_path}，但未找到窗口"
    except Exception as e:
        return False, f"启动应用失败: {e}"

@app.route('/api/window/maximize', methods=['POST'])
def api_maximize_window():
    """HTTP接口：最大化窗口"""
    data = request.get_json()
    window_title = data.get('title', '')
    if not window_title:
        return jsonify({'success': False, 'message': '请提供窗口标题'}), 400
    
    success, message = maximize_window(window_title)
    return jsonify({'success': success, 'message': message})

@app.route('/api/window/minimize', methods=['POST'])
def api_minimize_window():
    """HTTP接口：最小化窗口"""
    data = request.get_json()
    window_title = data.get('title', '')
    if not window_title:
        return jsonify({'success': False, 'message': '请提供窗口标题'}), 400
    
    success, message = minimize_window(window_title)
    return jsonify({'success': success, 'message': message})

@app.route('/api/window/activate', methods=['POST'])
def api_activate_window():
    """HTTP接口：激活窗口"""
    data = request.get_json()
    window_title = data.get('title', '')
    if not window_title:
        return jsonify({'success': False, 'message': '请提供窗口标题'}), 400
    
    success, message = activate_window(window_title)
    return jsonify({'success': success, 'message': message})

@app.route('/api/window/topmost', methods=['POST'])
def api_set_topmost():
    """HTTP接口：将窗口置顶"""
    data = request.get_json()
    window_title = data.get('title', '')
    if not window_title:
        return jsonify({'success': False, 'message': '请提供窗口标题'}), 400
    
    success, message = set_window_topmost(window_title)
    return jsonify({'success': success, 'message': message})

@app.route('/api/window/topmost/remove', methods=['POST'])
def api_remove_topmost():
    """HTTP接口：取消窗口置顶"""
    data = request.get_json()
    window_title = data.get('title', '')
    if not window_title:
        return jsonify({'success': False, 'message': '请提供窗口标题'}), 400
    
    success, message = remove_window_topmost(window_title)
    return jsonify({'success': success, 'message': message})

@app.route('/api/window/control', methods=['POST'])
def api_full_control():
    """HTTP接口：激活、最大化并置顶窗口"""
    data = request.get_json()
    window_title = data.get('title', '')
    if not window_title:
        return jsonify({'success': False, 'message': '请提供窗口标题'}), 400
    
    success, message = activate_maximize_topmost(window_title)
    return jsonify({'success': success, 'message': message})

@app.route('/api/browser/open', methods=['POST'])
def api_open_url():
    """HTTP接口：打开网页"""
    data = request.get_json()
    url = data.get('url', '')
    if not url:
        return jsonify({'success': False, 'message': '请提供URL'}), 400
    
    success, message = open_url(url)
    return jsonify({'success': success, 'message': message})

@app.route('/api/app/start', methods=['POST'])
def api_start_exe():
    """HTTP接口：启动应用"""
    data = request.get_json()
    exe_path = data.get('path', '')
    if not exe_path:
        return jsonify({'success': False, 'message': '请提供exe路径'}), 400
    
    success, message = start_exe(exe_path)
    return jsonify({'success': success, 'message': message})

@app.route('/api/windows/list', methods=['GET'])
def api_list_windows():
    """HTTP接口：获取所有窗口列表"""
    try:
        windows = gw.getAllWindows()
        window_list = [{'title': w.title, 'width': w.width, 'height': w.height} for w in windows if w.title]
        return jsonify({'success': True, 'windows': window_list})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def print_usage():
    """打印使用帮助"""
    print("Windows窗口控制工具")
    print("=" * 50)
    print("命令行模式:")
    print("  python window_controller.py --maximize <窗口标题>")
    print("  python window_controller.py --minimize <窗口标题>")
    print("  python window_controller.py --activate <窗口标题>")
    print("  python window_controller.py --topmost <窗口标题>")
    print("  python window_controller.py --topmost-remove <窗口标题>")
    print("  python window_controller.py --control <窗口标题>")
    print("  python window_controller.py --open-url <URL>")
    print("  python window_controller.py --start-exe <exe路径>")
    print("  python window_controller.py --list-windows")
    print()
    print("HTTP服务器模式:")
    print("  python window_controller.py --server")
    print("  然后通过HTTP API控制")
    print()
    print("HTTP API示例:")
    print("  POST /api/window/maximize -d '{\"title\": \"窗口标题\"}'")
    print("  POST /api/window/minimize -d '{\"title\": \"窗口标题\"}'")
    print("  POST /api/window/activate -d '{\"title\": \"窗口标题\"}'")
    print("  POST /api/window/topmost -d '{\"title\": \"窗口标题\"}'")
    print("  POST /api/window/topmost/remove -d '{\"title\": \"窗口标题\"}'")
    print("  POST /api/window/control -d '{\"title\": \"窗口标题\"}'")
    print("  POST /api/browser/open -d '{\"url\": \"https://example.com\"}'")
    print("  POST /api/app/start -d '{\"path\": \"C:/path/to/app.exe\"}'")
    print("  GET /api/windows/list")
    print()
    print("说明:")
    print("  --control: 同时激活、最大化并置顶窗口")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == '--maximize' and len(sys.argv) == 3:
        success, msg = maximize_window(sys.argv[2])
        print(msg)
    elif command == '--minimize' and len(sys.argv) == 3:
        success, msg = minimize_window(sys.argv[2])
        print(msg)
    elif command == '--activate' and len(sys.argv) == 3:
        success, msg = activate_window(sys.argv[2])
        print(msg)
    elif command == '--topmost' and len(sys.argv) == 3:
        success, msg = set_window_topmost(sys.argv[2])
        print(msg)
    elif command == '--topmost-remove' and len(sys.argv) == 3:
        success, msg = remove_window_topmost(sys.argv[2])
        print(msg)
    elif command == '--control' and len(sys.argv) == 3:
        success, msg = activate_maximize_topmost(sys.argv[2])
        print(msg)
    elif command == '--open-url' and len(sys.argv) == 3:
        success, msg = open_url(sys.argv[2])
        print(msg)
    elif command == '--start-exe' and len(sys.argv) == 3:
        success, msg = start_exe(sys.argv[2])
        print(msg)
    elif command == '--list-windows':
        try:
            windows = gw.getAllWindows()
            print("当前窗口列表:")
            for w in windows:
                if w.title:
                    print(f"  - {w.title}")
        except Exception as e:
            print(f"获取窗口列表失败: {e}")
    elif command == '--server':
        print("启动HTTP服务器...")
        print("服务器地址: http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("未知命令或参数错误")
        print_usage()