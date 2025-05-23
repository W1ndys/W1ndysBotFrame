# W1ndys-bot

![Python Version](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![NapCatQQ](https://img.shields.io/badge/Message-NapCatQQ-yellow)

基于 Python 和 [NapCatQQ](https://napneko.github.io/) 的 QQ 机器人实现。W1ndys 开发的 QQ 机器人，励志成为功能丰富，使用方便的 QQ 机器人。

**🔄 本项目的底层框架正在[W1ndysBotFrame](https://github.com/W1ndysBot/W1ndysBotFrame)重构，目前已完成。**

**本项目正在使用新的底层框架重构，开源在[W1ndysBot-dev](https://github.com/W1ndysBot/W1ndysBot-dev)，重构完成后会合并到本项目。**

## 流程图

```mermaid
graph TD
    A[程序启动] --> B[main.py]
    B --> C{连接机器人}

    C -->|成功| D[初始化日志系统]
    C -->|失败| E[钉钉通知]
    E --> F[等待1秒]
    F --> C

    D --> G[等待WebSocket消息]

    G --> H[handle_message]
    H --> I[解析JSON消息]

    I --> J[系统基础模块]
    J --> J1[System模块]
    J --> J2[Switch模块]

    I --> K[功能模块]
    K --> K1[BanWords2]
    K --> K2[ImageGenerate]
    K --> K3[SendAll]
    K --> K4[GroupManager]
    K --> K5[其他功能模块...]

    subgraph 模块内部处理
        L[模块handle_events]
        L --> M{消息类型判断}
        M -->|meta_event| N[处理元事件]
        M -->|message| O[处理消息]
        M -->|notice| P[处理通知]
        M -->|request| Q[处理请求]

        O --> R{消息类型}
        R -->|group| S[群消息处理]
        R -->|private| T[私聊处理]
    end

    G --> G
```

## 📚 开发文档

- [NapCatQQ 文档](https://napneko.github.io/)
- [NapCatQQ API](https://napcat.apifox.cn)

## 🔧 技术栈

- **核心开发**: Python
- **消息框架**: [NapCatQQ](https://napneko.github.io/)
- **机器人 API**: [NapCatQQ API](https://napcat.apifox.cn)

## 🌟 星标历史

[![Star History Chart](https://api.star-history.com/svg?repos=W1ndys/W1ndysBot&type=Date)](https://www.star-history.com/#W1ndys/W1ndysBot&Date)

## 📄 开源协议

本项目采用 [GPL-3.0](./LICENSE) 协议开源。

**重要提示**: 通过本项目所复制或衍生的作品，请遵守开源协议，并注明出处。
