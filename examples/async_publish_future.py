"""
示例: 异步发布消息MCP
- 演示如何使用MCP异步向设备发布Custom消息
! 注意需要类似示例完整定义各个函数的描述和参数Field描述, 确保FastMCP能正确解析工具内容并发送给LLM
! 在所有需要暴露给MCP的工具中, 必须定义system_args参数且mcp.tool修饰器中添加exclude_args=["system_args"], 该参数由MCP_CLIENT自动传入.
"""

from fastmcp import FastMCP
from pydantic import Field
import asyncio
import logging
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AsyncAction")
logger.addHandler(logging.StreamHandler())

# Create an MCP server
mcp = FastMCP("AsyncAction", host="0.0.0.0", port=9999)


async def async_action(
    message: str, 
    delay: int = 0,
    system_args: dict = {},
) -> str:
    """
    使用httpx异步发送请求给小智设备custom消息
    """
    mac_address:str = system_args.get("macAddress", "00:22:44:88:AA:CC")
    
    # 构建请求数据
    body = {
        "mac_address": mac_address.lower(),
        "type": "custom",
        "message": {
            "payload": {
                "message": message,
            }
        }
    }
    
    # HTTP请求头, 使用自行申请的token
    headers = {
        "authorization": "Bearer Your_Actual_Token_Here",
        "Content-Type": "application/json"
    }
    
    try:
        if delay > 0:
            logger.info(f"Delaying for {delay} seconds before sending message.")
            await asyncio.sleep(delay)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://xiaozhi.me/api/message/push",
                json=body,
                headers=headers,
                timeout=30.0
            )
            
            logger.info(f"HTTP Status: {response.status_code}")
            logger.info(f"Response: {response.text}")
            
            if response.status_code == 200:
                logger.info(f"Successfully sent message '{message}' to client:{mac_address}")
                return f"Message sent successfully. Response: {response.text}"
            else:
                logger.error(f"Failed to send message. Status: {response.status_code}, Response: {response.text}")
                return f"Failed to send message. Status: {response.status_code}"
                
    except Exception as e:
        logger.error(f"Error sending HTTP request: {e}")
        return f"Error sending message: {str(e)}"


@mcp.tool(exclude_args=["system_args"])
async def send_message(
    message: str = Field(description="str 要发送的消息内容"),
    delay: int = Field(default=0, description="int 延迟多少秒后发送消息, 默认立刻"),
    system_args: dict = Field(
        default_factory=dict,
        description="服务器参数, 必带且需要被exclude_args排除, 由服务器自动传入",
    ),
) -> dict:
    """
    向客户端异步发送消息
    """
    loop = asyncio.get_event_loop()
    loop.create_task(
        async_action(message, delay, system_args)
    )  # 在当前事件循环中运行协程
    logger.info("Scheduling task and return immediately.")
    return {"success":True, "result": "Message is being sent asynchronously."}


# Start the server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
