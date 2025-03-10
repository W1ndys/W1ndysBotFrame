import time
import hmac
import base64
import urllib.parse
import json
import subprocess
import requests
import asyncio
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# 钉钉机器人配置
WEBHOOK_URL = "https://oapi.dingtalk.com/robot/send?access_token=0c0ad4540eed1d1eab06d7229a573146430e6a8b5429eb4e3ada81e039987f6c"
SECRET = "SEC1000ac85e635258597301a211cde38a94644e10f473b110af6f2463e6008e441"


def get_signed_url():
    """生成带签名的钉钉webhook URL"""
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{SECRET}"
    hmac_code = hmac.new(
        SECRET.encode("utf-8"), string_to_sign.encode("utf-8"), digestmod="sha256"
    ).digest()

    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code).decode("utf-8"))
    return f"{WEBHOOK_URL}&timestamp={timestamp}&sign={sign}"


def get_container_logs():
    """获取Docker容器的最新日志"""
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", "50", "napcat"],
            capture_output=True,
            text=True,
        )
        return result.stdout.split("\n")
    except subprocess.CalledProcessError as e:
        logging.error(f"获取容器日志失败: {e}")
        return []


async def send_dingtalk_alert(text, desp=""):
    """异步发送钉钉告警消息"""
    try:
        timestamp = str(round(time.time() * 1000))
        secret_enc = SECRET.encode("utf-8")
        string_to_sign = f"{timestamp}\n{SECRET}"
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(
            secret_enc, string_to_sign_enc, digestmod="sha256"
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code).decode("utf-8"))

        url = f"{WEBHOOK_URL}&timestamp={timestamp}&sign={sign}"
        headers = {"Content-Type": "application/json"}
        payload = {"msgtype": "text", "text": {"content": f"{text}\n{desp}"}}

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        data = response.json()
        if response.status_code == 200 and data.get("errcode") == 0:
            logging.info("钉钉发送通知消息成功🎉")
        else:
            logging.error(f"钉钉发送通知消息失败😞\n{data.get('errmsg')}")

        return data
    except Exception as e:
        logging.error(f"钉钉发送通知消息失败😞\n{e}")
        raise


async def main():
    # 要监控的关键词
    keywords = ["账号状态变更为离线", "重新登录"]

    # 获取容器日志
    logs = get_container_logs()

    # 检查日志中的关键词
    alert_lines = []
    for line in logs:
        if any(keyword.lower() in line.lower() for keyword in keywords):
            alert_lines.append(line)

    # 如果发现异常日志，发送告警
    if alert_lines:
        text = "容器napcat发现异常日志"
        desp = "\n".join(alert_lines)
        await send_dingtalk_alert(text, desp)


if __name__ == "__main__":
    asyncio.run(main())
