# feishu_base.py
from mcp.server.fastmcp import FastMCP
import sys
import logging
import requests
import json

logger = logging.getLogger('FeishuBase')

# 飞书应用和多维表配置信息
APP_ID = "cli_adafdsafsafdfasd"  # 替换为实际的App ID
APP_SECRET = "iFydafdsfdsfsdafdsafdsfsafdsafff"  # 替换为实际的App Secret
APP_TOKEN = "YOadafsdfsafdasfdsgfdshgfdh"  # 替换为实际的多维表App Token
TABLE_ID = "tblgfdhgdfhdfhgf"  # 替换为实际的表ID
# 方法2：直接设置（仅用于测试，不推荐在生产环境使用）

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# Create an MCP server
mcp = FastMCP("FeishuBase")

class FeishuAPI:
    """飞书API操作类，用于处理飞书多维表的各种操作"""
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
        self.token = None
        self.token_expire_time = 0
    
    def get_token(self):
        """获取飞书API访问令牌"""
        import time
        # 如果令牌不存在或即将过期，则重新获取
        if not self.token or time.time() > self.token_expire_time - 300:
            url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
            headers = {"Content-Type": "application/json"}
            data = {"app_id": self.app_id, "app_secret": self.app_secret}
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            if result.get("code") == 0:
                self.token = result["tenant_access_token"]
                self.token_expire_time = time.time() + result["expire"]
            else:
                logger.error(f"获取飞书令牌失败: {result}")
                raise Exception(f"获取飞书令牌失败: {result}")
        return self.token
    
    def update_sheet_record(self, app_token, table_id, record_id, fields):
        """更新多维表中的记录"""
        token = self.get_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {"fields": fields}
        response = requests.put(url, headers=headers, json=data)
        result = response.json()
        if result.get("code") == 0:
            logger.info(f"更新多维表记录成功: {record_id}")
            return {"success": True, "data": result.get("data")}
        else:
            logger.error(f"更新多维表记录失败: {result}")
            return {"success": False, "error": result}
    
    def create_sheet_record(self, app_token, table_id, fields):
        """在多维表中创建新记录"""
        token = self.get_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {"fields": fields}
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        if result.get("code") == 0:
            logger.info(f"创建多维表记录成功")
            return {"success": True, "data": result.get("data")}
        else:
            # 添加详细的错误处理和建议
            error_message = f"创建多维表记录失败: {result}"
            logger.error(error_message)
            if result.get("code") == 91403:
                # 权限不足的错误码
                detailed_error = {
                    "success": False,
                    "error": result,
                    "suggestion": "权限不足，请确保您的飞书应用已添加以下权限并通过企业管理员审核：\n"
                                 "- bitable:app\n"
                                 "- bitable:app:readonly\n"
                                 "- bitable:record:read\n"
                                 "- bitable:record:write\n"
                                 "- bitable:table:read\n"
                                 "- bitable:table:write"
                }
                return detailed_error
            return {"success": False, "error": result}
    
    def batch_update_sheet_records(self, app_token, table_id, records):
        """批量更新多维表中的记录"""
        token = self.get_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {"records": records}
        response = requests.put(url, headers=headers, json=data)
        result = response.json()
        if result.get("code") == 0:
            logger.info(f"批量更新多维表记录成功")
            return {"success": True, "data": result.get("data")}
        else:
            logger.error(f"批量更新多维表记录失败: {result}")
            return {"success": False, "error": result}
    
    def query_sheet_records(self, app_token, table_id, filter=None, fields=None, sort=None, page_size=100):
        """查询多维表中的记录"""
        token = self.get_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/search"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {"page_size": page_size}
        if filter:
            # 确保filter参数包含必要的conjunction字段
            if isinstance(filter, dict):
                if "conjunction" not in filter:
                    # 默认设置为"and"，表示多个筛选条件之间为"与"关系
                    filter["conjunction"] = "and"
            data["filter"] = filter
        if fields:
            data["fields"] = fields
        if sort:
            # 检查并转换sort参数格式以符合飞书API要求
            if isinstance(sort, list):
                # 深拷贝以避免修改原始参数
                import copy
                processed_sort = copy.deepcopy(sort)
                for i, sort_item in enumerate(processed_sort):
                    if isinstance(sort_item, dict):
                        # 检查是否使用了'field'而不是'field_name'
                        if "field" in sort_item and "field_name" not in sort_item:
                            # 将'field'重命名为'field_name'
                            processed_sort[i]["field_name"] = processed_sort[i].pop("field")
                data["sort"] = processed_sort
            else:
                data["sort"] = sort
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        # 如果是排序字段不存在的错误（1254016），尝试不使用排序参数重新查询
        if result.get("code") == 1254016 and sort:
            logger.warning(f"排序字段不存在，尝试不使用排序参数重新查询: {result}")
            # 移除排序参数
            if "sort" in data:
                del data["sort"]
            # 重新发送请求
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if result.get("code") == 0:
                logger.info(f"不使用排序参数的查询成功")
                return {
                    "success": True,
                    "data": result.get("data"),
                    "warning": "原排序字段不存在，已使用无排序的方式完成查询。请检查排序字段名称是否正确。"
                }
        
        # 处理其他情况
        if result.get("code") == 0:
            logger.info(f"查询多维表记录成功")
            return {"success": True, "data": result.get("data")}
        else:
            logger.error(f"查询多维表记录失败: {result}")
            return {"success": False, "error": result}
            
    def check_permissions(self, app_token):
        """检查应用权限"""
        try:
            token = self.get_token()
            # 尝试读取一个简单的表信息来验证权限
            url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            response = requests.get(url, headers=headers)
            result = response.json()
            
            if result.get("code") == 0:
                logger.info(f"权限检查通过，当前应用有访问多维表的权限")
                return {"success": True, "message": "权限检查通过"}
            elif result.get("code") == 91403:
                logger.error(f"权限检查失败: 应用缺少必要的多维表权限")
                return {
                    "success": False,
                    "error": result,
                    "suggestion": "权限不足，请确保您的飞书应用已添加以下权限并通过企业管理员审核：\n"
                                 "- bitable:app\n"
                                 "- bitable:app:readonly\n"
                                 "- bitable:record:read\n"
                                 "- bitable:record:write\n"
                                 "- bitable:table:read\n"
                                 "- bitable:table:write"
                }
            else:
                logger.error(f"权限检查失败: {result}")
                return {"success": False, "error": result}
        except Exception as e:
            logger.error(f"权限检查时发生异常: {str(e)}")
            return {"success": False, "error": str(e)}

@mcp.tool()
def update_feishu_sheet_record(app_id: str = APP_ID, app_secret: str = APP_SECRET, app_token: str = APP_TOKEN, table_id: str = TABLE_ID, record_id: str = None, fields: dict = None) -> dict:
    """更新飞书多维表中的记录
    
    参数:
        app_id: 飞书应用的App ID
        app_secret: 飞书应用的App Secret
        app_token: 多维表应用的Token
        table_id: 多维表的表ID
        record_id: 要更新的记录ID
        fields: 要更新的字段和值，格式为{"字段名": "字段值"}
    
    返回:
        包含操作结果的字典
    """
    try:
        feishu = FeishuAPI(app_id, app_secret)
        return feishu.update_sheet_record(app_token, table_id, record_id, fields)
    except Exception as e:
        logger.error(f"更新飞书多维表记录时发生异常: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def create_feishu_sheet_record(app_id: str = APP_ID, app_secret: str = APP_SECRET, app_token: str = APP_TOKEN, table_id: str = TABLE_ID, fields: dict = None) -> dict:
    """在飞书多维表中创建新记录
    
    参数:
        app_id: 飞书应用的App ID
        app_secret: 飞书应用的App Secret
        app_token: 多维表应用的Token
        table_id: 多维表的表ID
        fields: 要设置的字段和值，格式为{"字段名": "字段值"}
    
    返回:
        包含操作结果的字典
    """
    try:
        feishu = FeishuAPI(app_id, app_secret)
        return feishu.create_sheet_record(app_token, table_id, fields)
    except Exception as e:
        logger.error(f"创建飞书多维表记录时发生异常: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def batch_update_feishu_sheet_records(app_id: str = APP_ID, app_secret: str = APP_SECRET, app_token: str = APP_TOKEN, table_id: str = TABLE_ID, records: list = None) -> dict:
    """批量更新飞书多维表中的记录
    
    参数:
        app_id: 飞书应用的App ID
        app_secret: 飞书应用的App Secret
        app_token: 多维表应用的Token
        table_id: 多维表的表ID
        records: 要更新的记录列表，格式为[{"record_id": "记录ID", "fields": {"字段名": "字段值"}}]
    
    返回:
        包含操作结果的字典
    """
    try:
        feishu = FeishuAPI(app_id, app_secret)
        return feishu.batch_update_sheet_records(app_token, table_id, records)
    except Exception as e:
        logger.error(f"批量更新飞书多维表记录时发生异常: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def query_feishu_sheet_records(app_id: str = APP_ID, app_secret: str = APP_SECRET, app_token: str = APP_TOKEN, table_id: str = TABLE_ID, filter: str = None, fields: list = None, sort: list = None, page_size: int = 100) -> dict:
    """查询飞书多维表中的记录
    
    参数:
        app_id: 飞书应用的App ID
        app_secret: 飞书应用的App Secret
        app_token: 多维表应用的Token
        table_id: 多维表的表ID
        filter: 过滤条件，遵循飞书API的过滤语法
        fields: 要返回的字段列表
        sort: 排序规则
        page_size: 每页返回的记录数
    
    返回:
        包含查询结果的字典
    """
    try:
        feishu = FeishuAPI(app_id, app_secret)
        return feishu.query_sheet_records(app_token, table_id, filter, fields, sort, page_size)
    except Exception as e:
        logger.error(f"查询飞书多维表记录时发生异常: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def check_feishu_permissions(app_id: str = APP_ID, app_secret: str = APP_SECRET, app_token: str = APP_TOKEN) -> dict:
    """检查飞书应用的多维表权限
    
    参数:
        app_id: 飞书应用的App ID
        app_secret: 飞书应用的App Secret
        app_token: 多维表应用的Token
    
    返回:
        包含权限检查结果的字典
    """
    try:
        feishu = FeishuAPI(app_id, app_secret)
        return feishu.check_permissions(app_token)
    except Exception as e:
        logger.error(f"检查飞书应用权限时发生异常: {str(e)}")
        return {"success": False, "error": str(e)}

# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")