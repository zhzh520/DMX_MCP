import os
import sys
import requests
import logging
from mcp.server.fastmcp import FastMCP

# ====================== 你的PearAPI真实密钥======================
#  API Key
PEAR_API_KEY = "3dbfdd7e8c23d006"
#  Private Key
PEAR_PRIVATE_KEY = "a02267f5-2fa9-46d8-a280-50d66c195e70"
HEADERS = {
    "token": PEAR_PRIVATE_KEY,
    "Content-Type": "application/json"
}

# ====================== MCP服务基础配置 ======================
mcp = FastMCP("MyCustomTools")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("PearMCP")


# ====================== 原有工具 完整保留 ======================
@mcp.tool()
def get_desktop_files() -> list:
    '''获取当前用户的桌面文件列表'''
    try:
        desktop_path = os.path.expanduser("~/Desktop")
        return os.listdir(desktop_path)
    except Exception as e:
        return [f"读取桌面失败：{str(e)}"]


@mcp.tool()
def calculator(a: float, b: float, operator: str) -> float:
    """执行基础数学运算（支持+-*/）
    Args:
        operator: 运算符，必须是'+','-','*','/'之一
    """
    if operator == '+':
        return a + b
    elif operator == '-':
        return a - b
    elif operator == '*':
        return a * b
    elif operator == '/':
        if b == 0:
            raise ZeroDivisionError("除数不能为0")
        return a / b
    else:
        raise ValueError("无效运算符")


# ===================== 【终极修复】PearAPI 今日油价接口（严格对标你后台截图！POST请求！） =====================
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


# ===================== PearAPI城际驾车路线接口（GET 请求，编码全兼容） =====================
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
# ====================== MCP固定启动入口 ======================
if __name__ == "__main__":
    logger.info("===== 自定义MCP服务启动成功 =====")
    mcp.run(transport='stdio')