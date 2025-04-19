#!/bin/bash

# 获取要搜索的目录，如果没有提供参数则使用默认目录
if [ -n "$1" ]; then
    TARGET_DIR="$1"
else
    TARGET_DIR="/home/bot/app/scripts"
fi

# 检查目录是否存在
if [ ! -d "$TARGET_DIR" ]; then
    echo "错误：目录 $TARGET_DIR 不存在！"
    exit 1
fi

echo "将在目录 $TARGET_DIR 中搜索Git相关文件"

# 定义要查找的Git相关文件
GIT_FILES=".git .gitignore .gitmodules .gitattributes"

# 构建查找命令
FIND_CMD="find $TARGET_DIR \("
first=true

for file in $GIT_FILES; do
    if [ "$first" = true ]; then
        FIND_CMD="$FIND_CMD -name \"$file\""
        first=false
    else
        FIND_CMD="$FIND_CMD -o -name \"$file\""
    fi
done
FIND_CMD="$FIND_CMD \)"

# 将结果保存到临时文件
TEMP_FILE=$(mktemp)
eval "$FIND_CMD" > "$TEMP_FILE"

# 检查是否找到文件
FILE_COUNT=$(wc -l < "$TEMP_FILE")

if [ "$FILE_COUNT" -eq 0 ]; then
    echo "没有找到任何Git相关文件！"
    rm "$TEMP_FILE"
    exit 0
fi

# 显示将要删除的文件
echo "以下Git相关文件将被删除："
cat "$TEMP_FILE"
echo "共找到 $FILE_COUNT 个文件"

# 确认删除
read -p "确认删除以上文件吗？(y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "取消删除"
    rm "$TEMP_FILE"
    exit 1
fi

# 执行删除操作
echo "正在删除文件..."
while read file; do
    rm -rf "$file"
    echo "已删除: $file"
done < "$TEMP_FILE"

rm "$TEMP_FILE"
echo "删除完成"
