import os
import tarfile
import requests
import json
import time
import subprocess
import datetime
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 飞书webhook地址
FEISHU_WEBHOOK_URL = (
    "https://open.feishu.cn/open-apis/bot/v2/hook/55648a44-6e84-4d8c-af16-30065ffba8c1"
)


def send_feishu_notification(title, content=""):
    """
    发送飞书通知
    :param title: 通知标题
    :param content: 通知内容
    :return: 响应结果
    """
    url = FEISHU_WEBHOOK_URL
    headers = {"Content-Type": "application/json"}

    # 使用文本类型消息
    payload = {"msg_type": "text", "content": {"text": f"{title}\n{content}"}}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        data = response.json()

        if response.status_code == 200 and data.get("code") == 0:
            logger.info("飞书通知发送成功🎉")
        else:
            logger.error(f"飞书通知发送失败😞\n{data.get('msg')}")

        return data
    except Exception as e:
        logger.error(f"飞书通知发送失败😞\n{e}")
        raise


def check_command_exists(command):
    """检查命令是否存在"""
    try:
        # 对于Windows和Unix系统使用不同的检查方法
        if os.name == "nt":  # Windows
            result = subprocess.run(
                f"where {command}", shell=True, capture_output=True, text=True
            )
            return result.returncode == 0
        else:  # Unix/Linux
            result = subprocess.run(
                f"which {command}", shell=True, capture_output=True, text=True
            )
            return result.returncode == 0
    except Exception:
        return False


def install_bypy():
    """安装bypy工具"""
    try:
        logger.info("正在安装bypy...")
        result = subprocess.run("pip install bypy", shell=True, check=True)
        logger.info("bypy安装成功！")
        logger.info("正在检查bypy是否可用...")

        # 用一个简单的命令测试bypy是否正常工作
        check_result = subprocess.run(
            "bypy --version", shell=True, capture_output=True, text=True
        )
        if check_result.returncode == 0:
            logger.info(f"bypy版本: {check_result.stdout.strip()}")
            logger.info("bypy已准备好使用！")
        else:
            logger.info("bypy安装成功，但可能需要重新打开终端才能使用。")
            logger.info("如果下一步出错，请关闭并重新打开终端，然后再次运行脚本。")

        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"安装失败: {e}")
        return False


def upload_file_to_baidu(local_file_path, remote_path="/"):
    """
    上传文件到百度网盘
    :param local_file_path: 本地文件路径
    :param remote_path: 百度网盘上的目标路径，默认为根目录
    :return: 上传结果
    """
    # 检查bypy是否安装
    if not check_command_exists("bypy"):
        logger.info("未检测到bypy命令。")
        install_choice = input("是否安装bypy? (y/n): ").lower()
        if install_choice == "y":
            if not install_bypy():
                return "错误：bypy安装失败，无法继续上传"
        else:
            return "错误：未安装bypy，无法继续上传"

    if not os.path.exists(local_file_path):
        return f"错误：文件 {local_file_path} 不存在"

    # 检查bypy是否已授权，添加超时机制
    logger.info("检查百度网盘授权状态...")
    try:
        # 使用超时机制避免命令无限等待
        auth_check = subprocess.run(
            "bypy info",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,  # 设置30秒超时
        )
        logger.info(f"授权检查输出: {auth_check.stdout}")
        logger.info(f"授权检查错误: {auth_check.stderr}")

        if "授权" in auth_check.stderr or "authorize" in auth_check.stderr.lower():
            logger.info("bypy需要授权，正在启动授权流程...")
            logger.info("请手动运行以下命令并按照提示完成授权:")
            logger.info("bypy info")
            proceed = input("授权完成后，输入'y'继续，输入其他退出: ")
            if proceed.lower() != "y":
                return "用户取消了操作"
        else:
            logger.info("bypy已授权，可以继续上传操作")

    except subprocess.TimeoutExpired:
        logger.info("授权检查超时。这可能意味着:")
        logger.info("1. bypy正在等待授权")
        logger.info("2. 网络连接问题")
        logger.info("请手动运行'bypy info'命令完成授权")
        proceed = input("授权完成后，输入'y'继续，输入其他退出: ")
        if proceed.lower() != "y":
            return "用户取消了操作"

    # 执行上传命令
    command = f"bypy upload {local_file_path} {remote_path}"
    try:
        logger.info(f"开始上传: {command}")
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            timeout=600,  # 10分钟超时
        )
        return f"上传成功：{result.stdout}"
    except subprocess.TimeoutExpired:
        return "上传操作超时，请检查网络连接或文件大小"
    except subprocess.CalledProcessError as e:
        # 如果是授权问题，提示用户进行授权
        if "授权" in e.stderr or "authorize" in e.stderr.lower():
            logger.info("需要进行百度网盘授权，请手动运行以下命令:")
            logger.info("bypy info")
            logger.info("并按照提示完成授权")
            proceed = input("授权完成后，输入'y'重试上传，输入其他退出: ")
            if proceed.lower() == "y":
                try:
                    # 重试上传
                    retry_result = subprocess.run(
                        command,
                        shell=True,
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=600,
                    )
                    return f"授权成功，上传完成：{retry_result.stdout}"
                except subprocess.CalledProcessError as retry_e:
                    return f"重试上传失败：{retry_e.stderr}"
                except subprocess.TimeoutExpired:
                    return "重试上传操作超时"
            else:
                return "用户取消了操作"
        return f"上传失败：{e.stderr}"


def backup_data_and_logs():
    """备份数据和日志"""
    # 进入/home/bot/app目录
    try:
        os.chdir("/home/bot/app")
    except Exception as e:
        logger.error("/home/bot/app 目录不存在或无法访问")
        return False

    # 检查data和logs目录是否存在
    if not os.path.exists("data") or not os.path.exists("logs"):
        logger.error("data 或 logs 目录不存在")
        return False

    # 获取当前日期和时间，使用连字符和冒号美化格式
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    archive_name = f"backup_data_and_logs_{current_datetime}.tar.gz"

    try:
        # 打包data和logs目录
        with tarfile.open(archive_name, "w:gz") as tar:
            tar.add("data")
            tar.add("logs")
        logger.info(f"打包成功: {archive_name}")

        # 获取文件完整路径
        archive_path = os.path.abspath(archive_name)
        return archive_path
    except Exception as e:
        logger.error(f"打包失败: {str(e)}")
        return False


def main():
    # 步骤1: 备份数据和日志
    archive_path = backup_data_and_logs()
    if not archive_path:
        send_feishu_notification("W1ndysBot备份失败", "备份数据和日志失败")
        return

    # 步骤2: 上传到百度网盘
    remote_dir = "/W1ndysBot/"
    file_name = os.path.basename(archive_path)
    remote_path = f"{remote_dir}{file_name}"

    result = upload_file_to_baidu(archive_path, remote_path)

    # 步骤3: 发送飞书通知
    if "上传成功" in result:
        send_feishu_notification(
            f"W1ndysBot备份数据上传百度网盘成功", f"文件名: {file_name}\n{result}"
        )
        # 删除本地文件
        try:
            os.remove(archive_path)
            logger.info(f"本地文件 {archive_path} 已删除")
        except Exception as e:
            logger.error(f"删除本地文件失败: {e}")
    else:
        send_feishu_notification(
            "W1ndysBot备份数据上传百度网盘失败", f"失败原因: {result}"
        )


if __name__ == "__main__":
    main()
