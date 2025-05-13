#!/bin/bash

# 默认目录
DEFAULT_DIR="/home/bot/app/scripts"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 使用用户提供的目录或默认目录
TARGET_DIR="${1:-$DEFAULT_DIR}"

# 检查目录是否存在
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}错误：目录 '$TARGET_DIR' 不存在${NC}"
    exit 1
fi

echo -e "${YELLOW}正在搜索Git相关文件，目录: $TARGET_DIR${NC}"

# 查找Git相关文件
git_files=()
while IFS= read -r -d $'\0' file; do
    git_files+=("$file")
done < <(find "$TARGET_DIR" \( -name ".git" -o -name ".gitignore" -o -name ".gitmodules" -o -name ".gitattributes" \) -print0)

# 显示结果
if [ ${#git_files[@]} -eq 0 ]; then
    echo -e "${GREEN}没有找到任何Git相关文件${NC}"
    exit 0
fi

echo -e "${YELLOW}找到以下Git相关文件 (共 ${#git_files[@]} 个):${NC}"
for file in "${git_files[@]}"; do
    echo "  $file"
done

# 确认删除
echo -e "${YELLOW}\n是否要删除这些文件? [y/N]${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${YELLOW}开始删除...${NC}"
    deleted_count=0
    for file in "${git_files[@]}"; do
        if [ -e "$file" ]; then
            if rm -rf "$file"; then
                echo -e "${GREEN}已删除: $file${NC}"
                ((deleted_count++))
            else
                echo -e "${RED}删除失败: $file${NC}"
            fi
        else
            echo -e "${YELLOW}文件不存在(可能已被删除): $file${NC}"
        fi
    done
    echo -e "${YELLOW}删除完成. 共删除 $deleted_count 个文件${NC}"
else
    echo -e "${GREEN}取消删除操作${NC}"
fi