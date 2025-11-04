#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书多维表工具使用示例

此脚本展示如何正确使用我们创建的飞书多维表工具，并解释各个参数的作用和来源。

重要提示：
1. 在运行脚本前，请确保您的飞书应用已添加必要的多维表权限并通过企业管理员审核
2. 这些权限包括：bitable:app, bitable:app:readonly, bitable:record:read, bitable:record:write, bitable:table:read, bitable:table:write
3. 请替换脚本中的占位符（如记录ID）为实际的值
"""

import os
import json

# 提示：在实际使用中，建议将敏感信息存储在环境变量或安全的配置文件中
# 不要直接在代码中硬编码这些信息

# 以下是各个参数的说明：
# 1. app_id 和 app_secret：从飞书开放平台获取的应用凭证
# 2. app_token：从飞书多维表界面或URL中获取的多维表应用Token
# 3. table_id：从飞书多维表界面或URL中获取的表ID

# 示例：如何设置这些参数
# 方法1：从环境变量中读取（推荐）
# app_id = os.environ.get('FEISHU_APP_ID')
# app_secret = os.environ.get('FEISHU_APP_SECRET')
# app_token = os.environ.get('FEISHU_APP_TOKEN')
# table_id = os.environ.get('FEISHU_TABLE_ID')

# 方法2：直接设置（仅用于测试，不推荐在生产环境使用）
app_id = "cli_adafdsafsafdfasd"  # 替换为实际的App ID
app_secret = "iFydafdsfdsfsdafdsafdsfsafdsafff"  # 替换为实际的App Secret
app_token = "YOadafsdfsafdasfdsgfdshgfdh"  # 替换为实际的多维表App Token
table_id = "tblgfdhgdfhdfhgf"  # 替换为实际的表ID

# 先检查权限状态
def check_permissions_first():
    """检查飞书应用权限状态"""
    from feishu_base import check_feishu_permissions
    permission_result = check_feishu_permissions(app_id, app_secret, app_token)
    if not permission_result.get('success'):
        print("\033[91m" + "权限检查失败！" + "\033[0m")
        if 'suggestion' in permission_result:
            print(permission_result['suggestion'])
        return False
    print("权限检查通过，继续执行操作...")
    return True

# 示例：如何调用查询记录的工具函数
# 在实际使用中，这些函数会被MCP框架自动调用，不需要手动调用
# 这里只是为了展示参数的传递方式
def example_query_records():
    """查询多维表记录示例"""
    # 导入我们创建的工具函数
    from feishu_base import query_feishu_sheet_records
    
    try:
        # 可选参数：过滤条件 - 注意：这里应该是字典对象，而不是字符串
        filter_condition = {"field": "状态", "operator": "=", "value": "未完成"}
        
        # 可选参数：要返回的字段列表
        fields = ["标题", "负责人", "截止日期", "状态"]
        
        # 可选参数：排序规则
        # 注意：请确保排序字段名称与您多维表中的实际字段名称一致
        # 如果遇到InvalidSort错误，请检查此字段名称是否存在
        sort = [{"field": "通用排序字段", "order": "asc"}]
        
        # 调用工具函数，注意app_token是作为参数传入的
        result = query_feishu_sheet_records(
            app_id=app_id,
            app_secret=app_secret,
            app_token=app_token,  # app_token在这里传入
            table_id=table_id,
            filter=filter_condition,
            fields=fields,
            sort=sort,
            page_size=20
        )
        
        print("查询结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 如果有警告信息，显示给用户
        if result.get('warning'):
            print("\033[93m" + f"警告: {result['warning']}" + "\033[0m")
    except Exception as e:
        print(f"查询多维表记录时发生异常: {str(e)}")

# 示例：如何查询客户名称字段
def example_query_customer_name():
    """查询客户名称字段示例"""
    # 导入我们创建的工具函数
    from feishu_base import query_feishu_sheet_records
    
    try:
        # 可选参数1：查询包含客户名称的所有记录
        # 在fields列表中包含"客户名称"字段，确保查询结果中返回该字段
        fields = ["标题", "负责人", "截止日期", "状态", "客户名称"]
        
        print("\n示例1：查询所有记录并返回包含客户名称的字段")
        # 不设置filter，查询所有记录
        result_all = query_feishu_sheet_records(
            app_id=app_id,
            app_secret=app_secret,
            app_token=app_token,
            table_id=table_id,
            fields=fields,
            page_size=20
        )
        
        print("查询结果:")
        print(json.dumps(result_all, ensure_ascii=False, indent=2))
        
        # 可选参数2：根据特定客户名称进行过滤查询
        print("\n示例2：根据特定客户名称过滤查询")
        # 将"特定客户名称"替换为实际的客户名称
        filter_by_customer = {"field": "客户名称", "operator": "=", "value": "特定客户名称"}
        
        result_filtered = query_feishu_sheet_records(
            app_id=app_id,
            app_secret=app_secret,
            app_token=app_token,
            table_id=table_id,
            filter=filter_by_customer,
            fields=fields,
            page_size=20
        )
        
        print(f"查询客户名称为'特定客户名称'的结果:")
        print(json.dumps(result_filtered, ensure_ascii=False, indent=2))
        
        # 如果有警告信息，显示给用户
        if result_all.get('warning'):
            print("\033[93m" + f"警告: {result_all['warning']}" + "\033[0m")
        if result_filtered.get('warning'):
            print("\033[93m" + f"警告: {result_filtered['warning']}" + "\033[0m")
        
    except Exception as e:
        print(f"查询客户名称字段时发生异常: {str(e)}")

# 示例：如何创建指定客户名称的记录
def example_create_customer_record():
    """创建指定客户名称的记录示例"""
    # 导入我们创建的工具函数
    from feishu_base import create_feishu_sheet_record
    
    try:
        print("\n创建客户名称为'i遥远的'的记录")
        
        # 要设置的字段和值
        fields = {
            "标题": "客户联系记录",
            "负责人": "当前用户",
            "截止日期": "2024-12-31",
            "状态": "未开始",
            "客户名称": "i遥远的",  # 设置指定的客户名称
            "备注": "这是通过API创建的客户记录"
        }
        
        # 调用工具函数，app_token作为参数传入
        result = create_feishu_sheet_record(
            app_id=app_id,
            app_secret=app_secret,
            app_token=app_token,
            table_id=table_id,
            fields=fields
        )
        
        print("创建结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if result.get('success'):
            print("\033[92m" + "成功创建客户名称为'i遥远的'的记录！" + "\033[0m")
            # 如果创建成功，可以调用查询函数来验证
            print("\n正在验证新创建的记录...")
            verify_record()
    except Exception as e:
        print(f"创建记录时发生异常: {str(e)}")

# 验证创建的记录
def verify_record():
    """验证创建的记录是否存在"""
    from feishu_base import query_feishu_sheet_records
    
    try:
        # 根据客户名称查询
        filter_condition = {"field": "客户名称", "operator": "=", "value": "i遥远的"}
        fields = ["标题", "负责人", "客户名称", "状态"]
        
        result = query_feishu_sheet_records(
            app_id=app_id,
            app_secret=app_secret,
            app_token=app_token,
            table_id=table_id,
            filter=filter_condition,
            fields=fields,
            page_size=1
        )
        
        if result.get('success') and result.get('data', {}).get('items'):
            items = result['data']['items']
            print(f"验证结果: 找到 {len(items)} 条客户名称为'i遥远的'的记录")
            if len(items) > 0:
                print(f"记录详情: {json.dumps(items[0], ensure_ascii=False, indent=2)}")
        else:
            print("\033[93m" + "验证结果: 未找到客户名称为'i遥远的'的记录" + "\033[0m")
    except Exception as e:
        print(f"验证记录时发生异常: {str(e)}")

# 示例：如何调用更新记录的工具函数
def example_update_record():
    """更新多维表记录示例"""
    # 导入我们创建的工具函数
    from feishu_base import update_feishu_sheet_record
    
    try:
        # 要更新的记录ID - 注意：需要替换为实际存在的记录ID
        print("提示：更新记录功能需要有效的记录ID")
        record_id = "rec_xxxxxxxxxxxx"  # 请替换为实际的记录ID
        
        if record_id == "rec_xxxxxxxxxxxx":
            print("\033[93m" + "警告：您正在使用示例记录ID，请替换为实际的记录ID！" + "\033[0m")
            return
        
        # 要更新的字段和值
        fields = {
            "状态": "已完成",
            "完成日期": "2023-12-31",
            "备注": "已完成任务"
        }
        
        # 调用工具函数，app_token作为参数传入
        result = update_feishu_sheet_record(
            app_id=app_id,
            app_secret=app_secret,
            app_token=app_token,  # app_token在这里传入
            table_id=table_id,
            record_id=record_id,
            fields=fields
        )
        
        print("更新结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"更新多维表记录时发生异常: {str(e)}")

# 示例：如何调用创建记录的工具函数
def example_create_record():
    """创建多维表记录示例"""
    # 导入我们创建的工具函数
    from feishu_base import create_feishu_sheet_record
    
    try:
        # 要设置的字段和值
        fields = {
            "标题": "新任务",
            "负责人": "张三",
            "截止日期": "2024-01-15",
            "状态": "未开始"
        }
        
        # 调用工具函数，app_token作为参数传入
        result = create_feishu_sheet_record(
            app_id=app_id,
            app_secret=app_secret,
            app_token=app_token,  # app_token在这里传入
            table_id=table_id,
            fields=fields
        )
        
        print("创建结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"创建多维表记录时发生异常: {str(e)}")

# 示例：如何调用批量更新记录的工具函数
def example_batch_update_records():
    """批量更新多维表记录示例"""
    # 导入我们创建的工具函数
    from feishu_base import batch_update_feishu_sheet_records
    
    try:
        # 要更新的记录列表
        print("提示：批量更新功能需要有效的记录ID")
        records = [
            {
                "record_id": "rec_xxxxxxxxxxxx1",  # 请替换为实际的记录ID
                "fields": {"状态": "进行中"}
            },
            {
                "record_id": "rec_xxxxxxxxxxxx2",  # 请替换为实际的记录ID
                "fields": {"状态": "已暂停"}
            }
        ]
        
        # 检查是否使用了示例记录ID
        if any(record["record_id"].startswith("rec_xxxx") for record in records):
            print("\033[93m" + "警告：您正在使用示例记录ID，请替换为实际的记录ID！" + "\033[0m")
            return
        
        # 调用工具函数，app_token作为参数传入
        result = batch_update_feishu_sheet_records(
            app_id=app_id,
            app_secret=app_secret,
            app_token=app_token,  # app_token在这里传入
            table_id=table_id,
            records=records
        )
        
        print("批量更新结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"批量更新多维表记录时发生异常: {str(e)}")

if __name__ == "__main__":
    print("飞书多维表工具使用示例\n")
    print("请注意：")
    print("1. 在使用前，请先替换脚本中的占位符为实际的值")
    print("2. app_token不是在代码中预设的，而是在调用工具函数时作为参数传入")
    print("3. 推荐将敏感信息存储在环境变量中，而不是硬编码在代码里")
    print("4. 在实际使用中，这些函数会被MCP框架自动调用，不需要手动调用\n")
    
    # 先检查权限状态
    if not check_permissions_first():
        print("\033[91m" + "权限不足，无法继续执行操作。请参考FEISHU_SETUP_GUIDE.md文档进行权限配置。" + "\033[0m")
        
    # 注意：由于存在权限问题和占位符ID，默认只执行查询操作以避免不必要的错误
    print("\n" + "\033[92m" + "注意：默认只执行查询操作，其他操作需要替换为实际的记录ID后再取消注释。" + "\033[0m")
    print("\n")
    
    # 执行查询操作
    example_query_records()
    
    # 执行查询客户名称字段的操作
    example_query_customer_name()
    
    # 注意：更新、创建和批量更新操作需要替换为实际的记录ID并拥有足够权限后再取消注释
    # example_update_record()
    # example_create_record()
    # example_batch_update_records()
    
    # 创建指定客户名称的记录
    # 注意：需要拥有足够的权限才能执行此操作
    # example_create_customer_record()