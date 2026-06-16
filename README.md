# NetWindowTrigger

Windows窗口控制工具，支持命令行和HTTP API远程控制。

## 功能特性

- 激活、最大化窗口
- 将窗口放到最上层
- 打开网页并自动最大化浏览器
- 启动exe应用并自动最大化
- HTTP API远程控制（局域网/公网）
- 搜索匹配窗口

## 安装

```bash
pip install -r requirements.txt
```

## 依赖

- pywin32 >= 306
- pygetwindow >= 0.0.9
- Flask >= 2.0.0

## 命令行使用

```bash
# 查看所有窗口
python window_controller.py --list-windows

# 激活并最大化窗口
python window_controller.py --control "窗口标题"

# 打开网页
python window_controller.py --open-url "https://www.baidu.com"

# 启动exe应用
python window_controller.py --start-exe "C:/path/to/app.exe"

# 最小化窗口
python window_controller.py --minimize "窗口标题"
```

## HTTP API 使用

启动服务器：
```bash
python window_controller.py --server
```

服务器启动后访问 http://localhost:5000

### API 接口

| 接口 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/api/windows/list` | GET | - | 获取所有窗口列表 |
| `/api/window/control` | POST | `{"title": "窗口标题"}` | 激活、最大化并放到最上层 |
| `/api/window/search` | POST | `{"title": "关键词"}` | 搜索匹配的窗口 |
| `/api/window/maximize` | POST | `{"title": "窗口标题"}` | 最大化窗口 |
| `/api/window/minimize` | POST | `{"title": "窗口标题"}` | 最小化窗口 |
| `/api/browser/open` | POST | `{"url": "https://..."}` | 打开网页 |
| `/api/app/start` | POST | `{"path": "C:/..."}` | 启动exe应用 |

### 局域网控制示例

```powershell
# Windows PowerShell
Invoke-RestMethod -Uri "http://192.168.x.x:5000/api/window/control" -Method POST -ContentType "application/json" -Body '{"title":"微信"}'

# Linux/Mac/Windows curl
curl -X POST http://192.168.x.x:5000/api/window/control -H "Content-Type: application/json" -d '{"title":"微信"}'
```

## 常见问题

### 中文窗口标题无法匹配
确保JSON使用UTF-8编码：
```powershell
Invoke-RestMethod -Uri "http://..." -ContentType "application/json; charset=utf-8" -Body '{"title":"微信"}'
```

### 防火墙阻止连接
```powershell
# Windows防火墙开放5000端口
netsh advfirewall firewall add rule name="NetWindowTrigger" dir=in action=allow protocol=tcp localport=5000
```

### 窗口标题查询
使用 `--list-windows` 或 `/api/windows/list` 查看当前所有窗口的标题。

## License

MIT
