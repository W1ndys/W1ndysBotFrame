import os
import subprocess
import sys
import time


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
        print("正在安装bypy...")
        result = subprocess.run("pip install bypy", shell=True, check=True)
        print("bypy安装成功！")
        print("正在检查bypy是否可用...")

        # 用一个简单的命令测试bypy是否正常工作
        check_result = subprocess.run(
            "bypy --version", shell=True, capture_output=True, text=True
        )
        if check_result.returncode == 0:
            print(f"bypy版本: {check_result.stdout.strip()}")
            print("bypy已准备好使用！")
        else:
            print("bypy安装成功，但可能需要重新打开终端才能使用。")
            print("如果下一步出错，请关闭并重新打开终端，然后再次运行脚本。")

        return True
    except subprocess.CalledProcessError as e:
        print(f"安装失败: {e}")
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
        print("未检测到bypy命令。")
        install_choice = input("是否安装bypy? (y/n): ").lower()
        if install_choice == "y":
            if not install_bypy():
                return "错误：bypy安装失败，无法继续上传"
        else:
            return "错误：未安装bypy，无法继续上传"

    if not os.path.exists(local_file_path):
        return f"错误：文件 {local_file_path} 不存在"

    # 检查bypy是否已授权，添加超时机制
    print("检查百度网盘授权状态...")
    try:
        # 使用超时机制避免命令无限等待
        auth_check = subprocess.run(
            "bypy info",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,  # 设置30秒超时
        )
        print(f"授权检查输出: {auth_check.stdout}")
        print(f"授权检查错误: {auth_check.stderr}")

        if "授权" in auth_check.stderr or "authorize" in auth_check.stderr.lower():
            print("bypy需要授权，正在启动授权流程...")
            print("请手动运行以下命令并按照提示完成授权:")
            print("bypy info")
            proceed = input("授权完成后，输入'y'继续，输入其他退出: ")
            if proceed.lower() != "y":
                return "用户取消了操作"
        else:
            print("bypy已授权，可以继续上传操作")

    except subprocess.TimeoutExpired:
        print("授权检查超时。这可能意味着:")
        print("1. bypy正在等待授权")
        print("2. 网络连接问题")
        print("请手动运行'bypy info'命令完成授权")
        proceed = input("授权完成后，输入'y'继续，输入其他退出: ")
        if proceed.lower() != "y":
            return "用户取消了操作"

    # 执行上传命令
    command = f"bypy upload {local_file_path} {remote_path}"
    try:
        print(f"开始上传: {command}")
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
            print("需要进行百度网盘授权，请手动运行以下命令:")
            print("bypy info")
            print("并按照提示完成授权")
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


# 使用示例
if __name__ == "__main__":
    file_to_upload = "/home/bot/app/backup_data_and_logs.tar.gz"
    result = upload_file_to_baidu(
        file_to_upload, "/W1ndysBot/backup_data_and_logs.tar.gz"
    )
    print(result)
