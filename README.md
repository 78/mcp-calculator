# MCP Sample Project | MCP 示例项目

A powerful interface for extending AI capabilities through remote control, calculations, email operations, knowledge search, and more.

一个强大的接口，用于通过远程控制、计算、邮件操作、知识搜索等方式扩展AI能力。

## Overview | 概述

MCP (Model Context Protocol) is a protocol that allows servers to expose tools that can be invoked by language models. Tools enable models to interact with external systems, such as querying databases, calling APIs, or performing computations. Each tool is uniquely identified by a name and includes metadata describing its schema.

MCP（模型上下文协议）是一个允许服务器向语言模型暴露可调用工具的协议。这些工具使模型能够与外部系统交互，例如查询数据库、调用API或执行计算。每个工具都由一个唯一的名称标识，并包含描述其模式的元数据。

## Features | 特性

- 🔌 Bidirectional communication between AI and external tools | AI与外部工具之间的双向通信
- 🔄 Automatic reconnection with exponential backoff | 具有指数退避的自动重连机制
- 📊 Real-time data streaming | 实时数据流传输
- 🛠️ Easy-to-use tool creation interface | 简单易用的工具创建接口
- 🔒 Secure WebSocket communication | 安全的WebSocket通信
- ⚙️ Multiple transport types support (stdio/sse/http) | 支持多种传输类型（stdio/sse/http）

## Quick Start | 快速开始

1. Install dependencies | 安装依赖:
```bash
pip install -r requirements.txt
```

2. Set up environment variables | 设置环境变量:
```bash
export MCP_ENDPOINT=<your_mcp_endpoint>
```

3. Run the calculator example | 运行计算器示例:
```bash
python mcp_pipe.py calculator.py
```

Or run all configured servers | 或运行所有配置的服务:
```bash
python mcp_pipe.py
```

*Requires `mcp_config.json` configuration file with server definitions (supports stdio/sse/http transport types)*

*需要 `mcp_config.json` 配置文件定义服务器（支持 stdio/sse/http 传输类型）*

## Project Structure | 项目结构

- `mcp_pipe.py`: Main communication pipe that handles WebSocket connections and process management | 处理WebSocket连接和进程管理的主通信管道
- `calculator.py`: Example MCP tool implementation for mathematical calculations | 用于数学计算的MCP工具示例实现
- `requirements.txt`: Project dependencies | 项目依赖

## Config-driven Servers | 通过配置驱动的服务

编辑 `mcp_config.json` 文件来配置服务器列表（也可设置 `MCP_CONFIG` 环境变量指向其他配置文件）。

配置说明：
- 无参数时启动所有配置的服务（自动跳过 `disabled: true` 的条目）
- 有参数时运行单个本地脚本文件
- `type=stdio` 直接启动；`type=sse/http` 通过 `python -m mcp_proxy` 代理

## Creating Your Own MCP Tools | 创建自己的MCP工具

Here's a simple example of creating an MCP tool | 以下是一个创建MCP工具的简单示例:

```python
from fastmcp import FastMCP

mcp = FastMCP("YourToolName")

@mcp.tool()
def your_tool(parameter: str) -> dict:
    """Tool description here"""
    # Your implementation
    return {"success": True, "result": result}

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## Use Cases | 使用场景

- Mathematical calculations | 数学计算
- Email operations | 邮件操作
- Knowledge base search | 知识库搜索
- Remote device control | 远程设备控制
- Data processing | 数据处理
- Custom tool integration | 自定义工具集成

## Requirements | 环境要求

- Python 3.7+
- websockets>=11.0.3
- python-dotenv>=1.0.0
- mcp>=1.8.1
- pydantic>=2.11.4
- mcp-proxy>=0.8.2

## Contributing | 贡献指南

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎贡献代码！请随时提交Pull Request。

## License | 许可证

This project is licensed under the MIT License - see the LICENSE file for details.

本项目采用MIT许可证 - 详情请查看LICENSE文件。

## Acknowledgments | 致谢

- Thanks to all contributors who have helped shape this project | 感谢所有帮助塑造这个项目的贡献者
- Inspired by the need for extensible AI capabilities | 灵感来源于对可扩展AI能力的需求
