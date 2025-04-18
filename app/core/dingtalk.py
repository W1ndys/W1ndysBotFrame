# 用于发送钉钉通知
import requests
import json
import time
import hmac
import hashlib
import urllib
import base64
import urllib.parse
import logging
import os


# 推送到钉钉
def dingtalk(text, desp):

    # 环境变量
    DD_BOT_URL = os.environ.get("DD_BOT_URL")
    DD_BOT_SECRET = os.environ.get("DD_BOT_SECRET")

    url = DD_BOT_URL
    headers = {"Content-Type": "application/json"}
    payload = {"msgtype": "text", "text": {"content": f"{text}\n{desp}"}}

    if DD_BOT_URL and DD_BOT_SECRET:
        timestamp = str(round(time.time() * 1000))
        secret_enc = DD_BOT_SECRET.encode("utf-8")
        string_to_sign = f"{timestamp}\n{DD_BOT_SECRET}"
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(
            secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(
            base64.b64encode(hmac_code).decode("utf-8").strip()
        )
        url = f"{url}&timestamp={timestamp}&sign={sign}"

        response = requests.post(url, headers=headers, data=json.dumps(payload))

    try:
        data = response.json()
        if response.status_code == 200 and data.get("errcode") == 0:
            logging.info("钉钉发送通知消息成功🎉")
        else:
            logging.error(f"钉钉发送通知消息失败😞\n{data.get('errmsg')}")
    except Exception as e:
        logging.error(f"钉钉发送通知消息失败😞\n{e}")

    return response.json()


if __name__ == "__main__":
    dingtalk("test", "test")
