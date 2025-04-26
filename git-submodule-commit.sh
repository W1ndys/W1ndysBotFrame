#!/bin/bash

# 保存主仓库路径
MAIN_REPO_PATH=$(pwd)
HAS_SUBMODULE_CHANGES=false

# 检查是否有子模块引用变更
SUBMODULE_CHANGES=$(git status -s | grep -E "^ M.*" | grep -v -E "(\.gitmodules)")

if [[ -n "$SUBMODULE_CHANGES" ]]; then
    echo "检测到子模块引用有更改，正在提交..."
    
    # 仅添加子模块引用变更，不添加其他修改的文件
    echo "$SUBMODULE_CHANGES" | awk '{print $2}' | while read submodule; do
        git add "$submodule"
    done
    
    # 添加 .gitmodules 文件如果有更改
    if [[ -n $(git status -s | grep -E "^ M.*\.gitmodules") ]]; then
        git add .gitmodules
    fi
    
    git commit -m "chore(子模块): 更新子模块引用"
    git push origin $(git symbolic-ref --short HEAD)
    
    echo "子模块引用更新已提交"
    HAS_SUBMODULE_CHANGES=true
else
    echo "没有检测到子模块引用变更"
fi

if [ "$HAS_SUBMODULE_CHANGES" = true ]; then
    echo "成功更新子模块引用"
else
    echo "没有子模块引用需要更新"
fi