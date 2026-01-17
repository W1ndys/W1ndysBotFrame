# 🤖 W1ndysBotFrame

![GitHub stars](https://img.shields.io/github/stars/W1ndys/W1ndysBotFrame?style=flat-square)
![GitHub forks](https://img.shields.io/github/forks/W1ndys/W1ndysBotFrame?style=flat-square)
![GitHub issues](https://img.shields.io/github/issues/W1ndys/W1ndysBotFrame?style=flat-square)
![GitHub license](https://img.shields.io/github/license/W1ndys/W1ndysBotFrame?style=flat-square)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/W1ndys/W1ndysBotFrame)

W1ndysBotFrame，一款基于 NapCat 和 Python 开发的 QQ 机器人框架。

## 📚 文档

- [开发指南](docs/development.md) - 模块开发详细教程
- [API 参考](docs/api-reference.md) - 完整的 API 接口文档

## ⚙️ 快速开始

### 环境要求

- Python 3.8+
- [NapCatQQ](https://github.com/NapNeko/NapCatQQ) 已部署并运行

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/W1ndys/W1ndysBotFrame.git
cd W1ndysBotFrame

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp app/.env.example app/.env
# 编辑 app/.env 文件填写配置

# 4. 运行机器人
python app/main.py
```

### 配置说明

编辑 `app/.env` 文件：

| 配置项 | 必填 | 说明 |
|--------|------|------|
| `OWNER_ID` | 是 | 机器人管理员 QQ 号 |
| `WS_URL` | 是 | NapCatQQ WebSocket 连接地址，如 `ws://127.0.0.1:3001` |
| `TOKEN` | 否 | 连接认证 token（需与 NapCat 配置一致） |
| `FEISHU_BOT_URL` | 否 | 飞书机器人 Webhook URL（用于掉线通知） |
| `FEISHU_BOT_SECRET` | 否 | 飞书机器人签名密钥 |

示例配置：

```env
OWNER_ID=123456789
WS_URL=ws://127.0.0.1:3001
TOKEN=your_token
```

## ✨ 功能特性

- ❤️ 心跳检测机器人在线状态
- 📢 掉线自动发送飞书通知
- 🔌 模块动态加载，无需修改核心代码
- 🔒 群聊/私聊功能开关独立控制
- ⏰ 支持定时任务
- 🔄 支持自动撤回消息
- 📨 私聊消息转达到管理员
- 📝 日志自动记录与清理
- 🧩 提供完整的模块开发模板

## 🛠️ 开发说明

详细的开发教程请参阅 [开发指南](docs/development.md)。

### 快速创建模块

1. 在 `app/modules/` 下创建模块目录
2. 参考 `app/modules/Template` 模板结构
3. 必须包含 `__init__.py` 和 `main.py`
4. `main.py` 中需要定义 `async handle_events(websocket, msg)` 函数

### 模块命名规范

如需为社区提供功能模块，请在自己的仓库中创建，命名为 `W1ndysBotFrame-Module-<功能名>`，便于框架用户搜索。

### 开发要点

- **数据存储**：在 `app/data/<模块名>/` 目录下存储数据
- **自动撤回**：消息 API 的 `note` 参数中添加 `del_msg=秒数`
- **异步编程**：使用 `asyncio.sleep()` 而非 `time.sleep()`
- **rkey 获取**：框架每 10 分钟自动刷新，存储在 `app/data/Core/nc_get_rkey.json`

### 开源协议

本项目采用 [GPL-3.0](LICENSE) 协议，请遵守开源协议。仅供学习交流使用，禁止用于非法用途。

## 更新方法

克隆新版本，覆盖原文件，重新运行即可

（注意备份好数据、日志、配置文件、自己开发的功能等，建议使用 git 管理，或复制新目录再覆盖）

```bash
git clone https://github.com/W1ndys/W1ndysBotFrame.git
```

## 🌟 星标历史

[![Star History Chart](https://api.star-history.com/svg?repos=W1ndys/W1ndysBotFrame&type=Date)](https://star-history.com/#W1ndys/W1ndysBotFrame&Date)
