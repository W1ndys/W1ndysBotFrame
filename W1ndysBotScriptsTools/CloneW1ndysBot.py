#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import re

###########################
# 该脚本由于部分Github仓库不开源，需要授权，导致克隆繁琐，本脚本暂时不使用
###########################


class BotCloner:
    def __init__(self):
        # 配置信息
        self.proxy_gateway = "ghfast.top"
        self.repo_url = "https://github.com/W1ndysBot/W1ndysBot"
        self.github_domain = "github.com"
        self.user_name = "W1ndys"
        self.proxy_url = "https://ghfast.top/"
        self.deploy_dir = "/home/bot"

        # 读取 GitHub Token
        self.github_token = self._read_github_token()

        # 修改为固定的临时目录
        self.temp_dir = "/tmp/w1ndysbot"

        # 检查并清理已存在的临时目录
        if os.path.exists(self.temp_dir):
            print(f"检测到已存在的临时目录，正在清理：{self.temp_dir}")
            shutil.rmtree(self.temp_dir)

    def _read_github_token(self):
        """读取 GitHub Token"""
        env_path = Path(".env")
        if not env_path.exists():
            print("错误：未找到 .env 文件，无法读取 GitHub Token")
            sys.exit(1)

        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=")[1].strip()
        return None

    def _run_command(self, command, cwd=None):
        """执行shell命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"命令执行失败: {e.cmd}")
            print(f"错误输出: {e.stderr}")
            return False

    def clone_main_repo(self):
        """克隆主仓库"""
        # 创建新的临时目录
        os.makedirs(self.temp_dir, exist_ok=True)
        os.chdir(self.temp_dir)

        # 显示调试信息
        print(f"正在尝试使用原始地址克隆...")

        # 修复URL格式，移除多余的斜杠
        original_clone_url = f"https://{self.user_name}:{self.github_token}@{self.github_domain}/{self.user_name}/W1ndysBot.git"
        print(f"实际使用的克隆命令：git clone {original_clone_url}")
        if self._run_command(f"git clone --depth 1 {original_clone_url}"):
            print("使用原始地址克隆成功")
            return

        # 如果原始地址失败，使用代理
        print("原始地址克隆失败，尝试使用代理...")
        clone_url = f"https://{self.user_name}:{self.github_token}@{self.proxy_gateway}/{self.repo_url}.git"
        if not self._run_command(f"git clone --depth 1 {clone_url}"):
            print("错误：主仓库克隆失败，请检查：")
            print(f"实际使用的克隆命令：git clone {clone_url}")
            print(f"建议手动测试：curl -I '{self.proxy_gateway}/{self.repo_url}'")
            sys.exit(1)
        print("使用代理克隆成功")

    def handle_submodules(self):
        """处理子模块"""
        os.chdir(f"{self.temp_dir}/W1ndysBot")

        if not Path(".gitmodules").exists():
            return

        with open(".gitmodules", "r") as f:
            content = f.read()

        # 解析子模块信息
        path_pattern = r"path\s*=\s*(.+)"
        url_pattern = r"url\s*=\s*(.+)"

        paths = re.findall(path_pattern, content)
        urls = re.findall(url_pattern, content)

        for submodule_path, original_url in zip(paths, urls):
            original_url = original_url.strip()
            submodule_path = submodule_path.strip()

            print(f"处理子模块：{original_url}")

            # 创建临时目录用于克隆子模块
            temp_submodule_path = f"{self.temp_dir}/temp_submodule_{submodule_path}"
            os.makedirs(temp_submodule_path, exist_ok=True)

            # 先尝试使用原始URL克隆
            if self._run_command(
                f"git clone --depth 1 {original_url} {temp_submodule_path}",
                cwd=f"{self.temp_dir}/W1ndysBot",
            ):
                print("使用原始地址克隆子模块成功")
            else:
                print("原始地址克隆失败，尝试使用代理...")
                # 转换子模块URL，处理格式
                proxied_sub_url = original_url.replace("https://github.com/", "", 1)
                proxied_sub_url = re.sub(r"\.git$", "", proxied_sub_url)
                proxied_sub_url = proxied_sub_url.strip("/")

                # 使用代理克隆
                clone_url = f"https://{self.user_name}:{self.github_token}@{self.proxy_gateway}/https://github.com/{proxied_sub_url}"
                if not self._run_command(
                    f"git clone --depth 1 {clone_url} {temp_submodule_path}",
                    cwd=f"{self.temp_dir}/W1ndysBot",
                ):
                    print(f"警告：子模块 {submodule_path} 克隆失败")
                    continue

            # 复制子模块文件（排除.git目录）到目标路径
            target_path = f"{self.temp_dir}/W1ndysBot/{submodule_path}"
            os.makedirs(target_path, exist_ok=True)
            self._run_command(
                f"rsync -av --delete --exclude='.git*' {temp_submodule_path}/ {target_path}/",
            )

            # 清理临时子模块目录
            shutil.rmtree(temp_submodule_path)

    def deploy(self):
        """部署到生产环境"""
        source_dir = f"{self.temp_dir}/W1ndysBot/"
        exclude_list = [".git*", "data", "logs"]
        exclude_args = " ".join(f"--exclude={item}" for item in exclude_list)

        self._run_command(
            f"rsync -av --delete {exclude_args} {source_dir} {self.deploy_dir}/"
        )

        # 清理临时文件
        os.chdir("/tmp")
        shutil.rmtree(self.temp_dir)

        # 执行重启脚本
        self._run_command(f"sh /home/bot/restart_app.sh")


def main():
    cloner = BotCloner()
    cloner.clone_main_repo()
    cloner.handle_submodules()
    cloner.deploy()
    print("部署成功！")


if __name__ == "__main__":
    main()
