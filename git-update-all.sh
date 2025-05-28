#!/bin/bash

# 设置输出颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 检查当前目录是否是 Git 仓库
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ 当前目录不是一个 Git 仓库。${NC}"
    exit 1
fi

echo -e "${BLUE}🔄 正在拉取主仓库的最新更改...${NC}"
git pull

echo -e "${BLUE}🔄 正在初始化子模块...${NC}"
git submodule update --init --recursive

echo -e "${BLUE}🔄 正在更新子模块到 main 分支...${NC}"
git submodule foreach 'git checkout main && git pull --depth=1 origin main'

echo -e "${BLUE}🔍 检查子模块状态...${NC}"
# 获取所有子模块路径
SUBMODULES=$(git submodule status | awk '{print $2}')

# 检查并更新有改动的子模块
UPDATED_COUNT=0
for SUBMODULE in $SUBMODULES; do
    echo -e "${BLUE}检查子模块: ${SUBMODULE}${NC}"
    
    # 进入子模块目录
    cd "$SUBMODULE" || continue
    
    # 检查远程是否有更新
    git fetch origin main &>/dev/null
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)
    
    # 如果本地和远程不一致，则有更新
    if [ "$LOCAL" != "$REMOTE" ]; then
        echo -e "${YELLOW}📥 子模块 ${SUBMODULE} 有更新，正在更新...${NC}"
        git checkout main && git pull --depth=1 origin main
        UPDATED_COUNT=$((UPDATED_COUNT + 1))
    else
        echo -e "${GREEN}✓ 子模块 ${SUBMODULE} 已是最新${NC}"
    fi
    
    # 返回主目录
    cd - &>/dev/null
done

if [ $UPDATED_COUNT -gt 0 ]; then
    echo -e "${GREEN}✅ 已更新 ${UPDATED_COUNT} 个子模块。${NC}"
else
    echo -e "${GREEN}✅ 所有子模块均为最新状态。${NC}"
fi
