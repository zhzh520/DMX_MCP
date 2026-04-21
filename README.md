# 开发自己的MCP服务

本项目基于 FastMCP 框架，实现自定义 MCP（Model Control Protocol）服务搭建，通过标准化协议将本地工具函数暴露给 AI 客户端（本文以 Cursor 编辑器为例），实现 AI 自然语言指令与本地代码的联动调用。核心提供文件系统查询、基础运算能力，并支持模块化扩展，兼顾实用性与可扩展性，适用于本地 AI 工具定制、私有服务部署场景。

## 1. 环境准备

### 1.1 前置依赖

| 依赖项   | 版本要求   | 安装方式                 | 说明                                         |
| :------- | :--------- | :----------------------- | :------------------------------------------- |
| Python   | 3.9+       | 官网下载或 Anaconda 安装 | 建议使用 3.10 版本，保障依赖兼容性           |
| Anaconda | 2023.09+   | 官网下载                 | 用于创建独立虚拟环境，隔离项目依赖           |
| FastMCP  | 最新稳定版 | pip install fastmcp      | MCP 服务核心框架，提供工具注册与协议通信能力 |
| Cursor   | 最新版     | 官网下载                 | MCP 客户端，用于调用自定义服务               |

### 1.2 虚拟环境配置

```bash
# 1. 创建虚拟环境（环境名：MCP，Python 版本 3.10）
conda create -n MCP python=3.10 -y

# 2. 激活虚拟环境
conda activate MCP

# 3. 验证环境（确认 Python 路径为虚拟环境路径）
where python  # Windows 系统
which python  # Linux/Mac 系统

# 4. 安装核心依赖
pip install fastmcp -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 2. 核心代码实现

### 2.1 服务核心代码（test.py）

基于 FastMCP 框架，实现工具注册、服务初始化与启动，代码如下（含详细技术注释）：

```
import os
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("FileSystem") # 服务名称
@mcp.tool()
def get_desktop_files() -> list:
    '''获取当前用户的桌面文件列表'''
    return os.listdir(os.path.expanduser("~/Desktop"))
@mcp.tool()
def calculator(a: float, b: float, operator: str) -> float:
    """执行基础数学运算（支持+-*/）
    Args:
    operator: 运算符，必须是'+','-','*','/'之一
    """
    if operator == '+': return a + b
    elif operator == '-': return a - b
    elif operator == '*': return a * b
    elif operator == '/': return a / b
    else: raise ValueError("无效运算符")
if __name__ == "__main__":
    mcp.run(transport='stdio') # 使用标准输入输出通信
```

启动代码并进入mcp服务器后台

```
python test.py
mcp dev test.py
```

### 2.2进行调试

连接成功后，在右侧 **Tools** 标签页操作：

1. 点击 

   List Tools

   ，你会看到两个注册好的工具：

   - `get_desktop_files`（无参数，获取桌面文件）
   - `calculator`（需传入 a、b、operator 三个参数）

<img width="830" height="464" alt="屏幕截图 2026-04-21 145137" src="https://github.com/user-attachments/assets/bdfaac1c-8615-41b6-a1ed-4065d6d71f9b" />


2. 测试 

   ```
   calculator
   ```

    工具：

   - 选中该工具，在参数输入框中填写：

     ```json
     {"a": 10, "b": 2, "operator": "*"}
     ```

   - 点击 **Run Tool**，下方会返回计算结果（如 20.0），证明工具正常运行。

<img width="1704" height="812" alt="屏幕截图 2026-04-20 221111" src="https://github.com/user-attachments/assets/80c0d2c9-5e6a-4535-8b90-f6b906a31452" />


### 2.3 调试注意事项

- 调试前需确保虚拟环境已激活，且依赖已正确安装。
- 若调试页面无法打开，检查 localhost:6277 端口是否被占用，可通过「netstat -ano | findstr 6277」（Windows）查看端口占用情况，关闭占用进程后重新启动调试服务。
- 工具函数修改后，需重启调试服务才能生效。

## 3. Cursor 客户端接入配置

### 3.1 配置文件说明

Cursor 客户端通过 mcp.json 配置文件管理 MCP 服务，该文件存储所有已接入的 MCP 服务信息，包括服务标识、启动命令、参数等，配置遵循 JSON 规范。

### 3.2 完整配置内容

在 mcp.json 文件的「mcpServers」节点下，添加自定义 MCP 服务配置，兼容已接入的第三方 MCP 服务（如高德地图、12306），配置如下：

```json
{
  "mcpServers": {
    "amap-maps": {
      "command": "npx",
      "args": [
        "-y",
        "@amap/amap-maps-mcp-server"
      ],
      "env": {
        "AMAP_MAPS_API_KEY": "467e0423b677e743e04022a72596b8f5"
      }
    },
    "my-file-mcp": {
      "command": "C:/Users/huihu/anaconda3/envs/MCP/python.exe",
      "args": [
        "D:/Users/huihu/Desktop/2026/damoxing/MCP/test.py"
      ]
    },
    "12306-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "12306-mcp"
      ]
    }
  }
}
```

| 参数名      | 类型   | 说明                                                         |
| :---------- | :----- | :----------------------------------------------------------- |
| command     | string | 虚拟环境中 Python 可执行文件的绝对路径，用于启动 MCP 服务    |
| args        | array  | 启动参数，第一个元素为核心服务文件（mcp_service.py）的绝对路径，后续可添加额外参数（如日志级别） |
| env         | object | 环境变量配置，本项目无需额外环境变量，留空即可               |
| description | string | 服务描述，用于 Cursor 客户端展示，可选                       |

<img width="986" height="395" alt="屏幕截图 2026-04-20 221436" src="https://github.com/user-attachments/assets/0ab5624f-2336-4f37-99ff-7cfae44137f9" />


## 3.4 配置验证与服务启用

1. 配置完成后，保存 mcp.json 文件，关闭并重新打开 Cursor 编辑器。
2. 进入 Cursor 配置页面：点击左下角「设置」→ 选择「Tools & MCPs」。
3. 在服务列表中找到「custom-local-tools」，开启右侧开关，此时开关显示绿色，且下方显示「2 tools enabled」（对应注册的两个工具函数），表示服务接入成功。
4. 若开关显示红色或提示“无法连接”，检查配置文件中的 Python 路径、服务文件路径是否正确，路径分隔符统一使用「/」或「\\」，避免使用单个「\」。

## 4. 工具扩展指南

### 4.1 扩展原则

- 遵循模块化设计，每个工具函数实现单一功能，便于维护和测试。
- 工具函数需添加完整的文档字符串（docstring），明确入参、返回值、异常信息，确保 AI 能正确解析工具用途。
- 所有工具函数需通过 @mcp.tool() 装饰器注册，才能被 MCP 服务识别和暴露。

### 4.2 扩展模板

```
@mcp.tool()
def 你的工具名(参数1: 类型, 参数2: 类型) -> str:
    """工具说明（AI 能看懂）
    Args:
        参数1: 说明
        参数2: 说明
    """
    # 1. 请求地址
    api_url = "https://你的api地址"
    
    # 2. 请求参数（按接口要求写）
    request_json = {
        "key1": 参数1,
        "key2": 参数2
    }

    try:
        # 3. 发送请求
        resp = requests.post(
            url=api_url,
            json=request_json,
            headers=HEADERS,
            timeout=15
        )

        # 4. 解析 JSON
        resp_data = resp.json()

        # 5. 判断是否成功
        if resp_data.get("code") != 200:
            return f"失败：{resp_data.get('msg')}"

        # 6. 成功 → 格式化返回给 AI
        data = resp_data["data"]
        return f"格式化好的结果字符串"

    except Exception as e:
        return f"请求异常：{str(e)}"
```

我这里是扩展了一个查询各地油价和城际驾车路线的工具（前面要调用Pear API的API Key）

```
# ===================== PearAPI 今日油价接口 =====================
@mcp.tool()
def get_oil_price_pear(province: str) -> str:
    """
    Query latest oil price of province in China (PearAPI Official)
    Args:
        province: province name, e.g. Sichuan, Guangdong, Beijing, Shanghai
    """
    api_url = "https://api.pearktrue.cn/api/oil/price"
    # 100%还原你后台接口的请求体JSON格式！！！
    request_json = {
        "type": "get",
        "province": province
    }

    try:
        # 重点根治：接口原生是 POST 请求！用json传参！携带完整鉴权头！
        response = requests.post(
            url=api_url,
            json=request_json,
            headers=HEADERS,
            timeout=15
        )
        response.encoding = "utf-8"
        
        # ========== 调试日志：终端会打印接口原始返回，一眼定位问题 ==========
        print(f"\n[Oil API Debug Info]")
        print(f"Request URL: {api_url}")
        print(f"Request Body: {request_json}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Raw Text: {response.text}\n")

        # 空响应兜底，根治 char 0 解析报错
        if not response.text.strip():
            return (
                "Error: Oil API returned EMPTY response!\n"
                "Please check: 1. Your PearAPI API Key is CORRECT & fully pasted\n"
                "2. Your account has remaining call quota\n"
                "3. Network connection to PearAPI server is normal"
            )
        
        resp_json = response.json()
        if resp_json.get("code") != 200:
            return f"Oil Query Failed: {resp_json.get('msg', 'Platform error')}"
        
        data = resp_json["data"]
        return (
            f"[{data['province_prt_name']} Today Oil Price]\n"
            f"92# Gasoline: {data['province_price_92']}\n"
            f"95# Gasoline: {data['province_price_95']}\n"
            f"98# Gasoline: {data['province_price_98']}\n"
            f"0# Diesel: {data['province_price_diesel_0']}\n"
            f"Last Update: {data['time']}\n"
            f"Next Price Adjust: {data['next_update_time']}"
        )
    except Exception as e:
        return f"Oil Request Error: {str(e)}"

# ===================== PearAPI城际驾车路线接口=====================
@mcp.tool()
def get_city_route(from_city: str, to_city: str) -> str:
    """
    Query driving route info between two cities (distance, time, cost)
    Args:
        from_city: start city, e.g. Guangzhou
        to_city: destination city, e.g. Shenzhen
    """
    api_url = "https://api.pearktrue.cn/api/citytravelroutes/"
    params = {
        "from": from_city,
        "to": to_city
    }
    try:
        resp = requests.get(url=api_url, params=params, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        print(f"[Route Debug] Raw response: {resp.text}")
        
        if not resp.text.strip():
            return "Error: Route API empty response, check API Key & network"
        
        resp_json = resp.json()
        if resp_json.get("code") != 200:
            return f"Route Query Failed: {resp_json.get('msg')}"
        
        data = resp_json["data"]
        return (
            f"[Driving Route: {from_city} → {to_city}]\n"
            f"Total Distance: {data['distance']}\n"
            f"Estimated Time: {data['time']}\n"
            f"Fuel Cost: {data['fuelcost']}\n"
            f"Toll Fee: {data['bridgetoll']}\n"
            f"Total Cost: {data['totalcost']}"
        )
    except Exception as e:
        return f"Route Interface Error: {str(e)}"
```

### 最后进行展示

<img width="1421" height="767" alt="屏幕截图 2026-04-21 143938" src="https://github.com/user-attachments/assets/ef2d146a-4866-436c-be38-502f5cd372c1" />


<img width="535" height="244" alt="屏幕截图 2026-04-21 144006" src="https://github.com/user-attachments/assets/6c2e02d3-8817-4c62-ae31-86e8d2422196" />

<img width="1340" height="927" alt="屏幕截图 2026-04-20 215710" src="https://github.com/user-attachments/assets/9ed76d5a-3cf9-4353-bd0a-fba39d58dbec" />
