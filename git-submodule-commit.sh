#!/bin/bash

# 保存主仓库路径
MAIN_REPO_PATH=$(pwd)
UPDATED=false

# 先检查主仓库中是否有子模块引用的变更
if [[ -n $(git status -s | grep -E "^ M.*") ]]; then
    echo "检测到子模块引用有更改，正在提交..."
    
    # 添加所有已修改的子模块引用
    git add $(git status -s | grep -E "^ M" | awk '{print $2}')
    git commit -m "chore(子模块): 更新子模块引用"
    git push origin $(git symbolic-ref --short HEAD)
    
    echo "子模块引用更新已提交"
    UPDATED=true
fi

# 遍历所有子模块检查内部更改
echo "开始检查所有子模块内部更改..."
git submodule foreach --recursive '
    # 检查子模块是否有未提交更改
    if [[ -n $(git status -s) ]]; then
        SUBMODULE_NAME=$(basename $(pwd))
        echo "子模块 $SUBMODULE_NAME 有内部更改，正在提交..."
        
        # 在子模块中添加、提交更改
        git add .
        git commit -m "feat($SUBMODULE_NAME): 自动更新子模块内容"
        git push
        
        # 设置更新标志
        cd $MAIN_REPO_PATH
        git add $(pwd | sed "s|$MAIN_REPO_PATH/||")
        UPDATED=true
    else
        echo "子模块 $(basename $(pwd)) 没有内部更改，跳过"
    fi
'

# 如果在遍历子模块过程中有更新，提交主仓库中的子模块引用变更
if [ "$UPDATED" = true ] && [[ -n $(git status -s) ]]; then
    echo "提交主仓库中的子模块引用更新..."
    git commit -m "chore(子模块): 更新子模块引用"
    git push origin $(git symbolic-ref --short HEAD)
    echo "所有子模块更新完成并已同步到主仓库"
elif [ "$UPDATED" = true ]; then
    echo "子模块更新已完成"
else
    echo "没有发现需要更新的子模块"
fi