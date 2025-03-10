#!/bin/bash

###########################
# 该脚本由于部分Github仓库不开源，需要授权，导致克隆繁琐，本脚本暂时不使用
###########################


# 配置信息
PROXY_GATEWAY="ghfast.top"
REPO_URL="https://github.com/W1ndysBot/W1ndysBot"
GITHUB_DOMAIN="github.com"
USER_NAME="W1ndys"
PROXY_URL="https://ghfast.top/"
DEPLOY_DIR="/home/bot"
TEMP_DIR="/tmp/w1ndysbot"

# 移除 Git 全局代理设置
echo "正在移除 Git 全局代理设置..."
git config --global --unset http.proxy
git config --global --unset https.proxy

# 读取 GitHub Token
if [ ! -f .env ]; then
    echo "错误：未找到 .env 文件，无法读取 GitHub Token"
    exit 1
fi

GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" .env | cut -d'=' -f2)

# 检查并清理已存在的临时目录
if [ -d "$TEMP_DIR" ]; then
    echo "检测到已存在的临时目录，正在清理：$TEMP_DIR"
    rm -rf "$TEMP_DIR"
fi

# 创建新的临时目录
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR" || exit 1

# 克隆主仓库
echo "正在尝试使用原始地址克隆..."
ORIGINAL_CLONE_URL="https://$USER_NAME:$GITHUB_TOKEN@$GITHUB_DOMAIN/$USER_NAME/W1ndysBot.git"
echo "实际使用的克隆命令：git clone $ORIGINAL_CLONE_URL"

if git clone --depth 1 "$ORIGINAL_CLONE_URL"; then
    echo "使用原始地址克隆成功"
else
    echo "原始地址克隆失败，尝试使用代理..."
    CLONE_URL="https://$USER_NAME:$GITHUB_TOKEN@$PROXY_GATEWAY/$REPO_URL.git"
    if ! git clone --depth 1 "$CLONE_URL"; then
        echo "错误：主仓库克隆失败，请检查："
        echo "实际使用的克隆命令：git clone $CLONE_URL"
        echo "建议手动测试：curl -I '$PROXY_GATEWAY/$REPO_URL'"
        exit 1
    fi
    echo "使用代理克隆成功"
fi

# 处理子模块
cd "$TEMP_DIR/W1ndysBot" || exit 1

if [ -f .gitmodules ]; then
    while IFS= read -r line; do
        if [[ $line =~ path[[:space:]]*=[[:space:]]*(.+) ]]; then
            SUBMODULE_PATH="${BASH_REMATCH[1]}"
            SUBMODULE_PATH=$(echo "$SUBMODULE_PATH" | xargs)
        elif [[ $line =~ url[[:space:]]*=[[:space:]]*(.+) ]]; then
            ORIGINAL_URL="${BASH_REMATCH[1]}"
            ORIGINAL_URL=$(echo "$ORIGINAL_URL" | xargs)
            
            echo "处理子模块：$ORIGINAL_URL"
            TEMP_SUBMODULE_PATH="$TEMP_DIR/temp_submodule_$SUBMODULE_PATH"
            mkdir -p "$TEMP_SUBMODULE_PATH"

            if git clone --depth 1 "$ORIGINAL_URL" "$TEMP_SUBMODULE_PATH"; then
                echo "使用原始地址克隆子模块成功"
            else
                echo "原始地址克隆失败，尝试使用代理..."
                PROXIED_SUB_URL=$(echo "$ORIGINAL_URL" | sed 's|https://github.com/||' | sed 's|\.git$||' | sed 's|/$||')
                CLONE_URL="https://$USER_NAME:$GITHUB_TOKEN@$PROXY_GATEWAY/https://github.com/$PROXIED_SUB_URL"
                
                if ! git clone --depth 1 "$CLONE_URL" "$TEMP_SUBMODULE_PATH"; then
                    echo "警告：子模块 $SUBMODULE_PATH 克隆失败"
                    continue
                fi
            fi

            TARGET_PATH="$TEMP_DIR/W1ndysBot/$SUBMODULE_PATH"
            mkdir -p "$TARGET_PATH"
            rsync -av --delete --exclude='.git*' "$TEMP_SUBMODULE_PATH/" "$TARGET_PATH/"
            rm -rf "$TEMP_SUBMODULE_PATH"
        fi
    done < .gitmodules
fi

# 部署到生产环境
SOURCE_DIR="$TEMP_DIR/W1ndysBot/"
rsync -av --delete --exclude='.git*' --exclude='data' --exclude='logs' "$SOURCE_DIR" "$DEPLOY_DIR/"

# 清理临时文件
cd /tmp || exit 1
rm -rf "$TEMP_DIR"

# 执行重启脚本
sh /home/bot/restart_app.sh

echo "部署成功！" 