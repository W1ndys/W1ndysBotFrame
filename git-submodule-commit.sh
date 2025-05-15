#!/bin/bash

# 询问是否需要添加所有文件，默认回车添加所有文件
read -p "是否需要添加所有文件？(y/n，默认y): " add_all

if [ -z "$add_all" ] || [ "$add_all" = "y" ]; then
    git add .
else
    echo "请手动添加需要提交的文件后继续"
    exit 1
fi

# 提交更改，提交信息为"更新子模块"
git commit -m "chore(子模块): 更新子模块"

# 推送到远程仓库的当前分支
git push origin $(git symbolic-ref --short HEAD)

echo "已成功提交并推送更改"