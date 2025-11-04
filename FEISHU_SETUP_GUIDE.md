# 飞书开放平台应用配置指南

本指南将详细说明如何在飞书开放平台注册应用、获取必要的凭证和权限，以及如何找到多维表相关的参数。

## 一、注册飞书开放平台账号并创建应用

1. **访问飞书开放平台**
   - 打开浏览器，访问 [飞书开放平台](https://open.feishu.cn/)
   - 使用您的飞书账号登录

2. **创建企业自建应用**
   - 登录后，点击顶部导航栏的「开发者后台」
   - 在左侧菜单中选择「应用列表」
   - 点击「创建企业自建应用」按钮
   - 填写应用名称（例如："多维表操作工具"）和应用描述
   - 选择应用类型为「机器人」
   - 点击「创建」按钮

3. **获取App ID和App Secret**
   - 应用创建成功后，进入应用详情页
   - 在「凭证与基础信息」页面，您可以找到App ID和App Secret
   - 点击「重置」按钮可以生成新的App Secret（请妥善保管，只显示一次）

## 二、配置应用权限

1. **进入权限管理页面**
   - 在应用详情页左侧菜单中选择「权限管理」

2. **添加多维表相关权限**
   - 在搜索框中搜索并添加以下权限：
     - `bitable:app` - 读取、写入多维表格应用信息
     - `bitable:app:readonly` - 只读访问多维表格应用信息
     - `bitable:record:read` - 读取多维表格记录
     - `bitable:record:write` - 写入多维表格记录
     - `bitable:table:read` - 读取多维表格表结构
     - `bitable:table:write` - 写入多维表格表结构
   - 点击「添加」按钮将这些权限添加到应用

3. **申请权限**
   - 添加完权限后，点击「申请权限」按钮
   - 填写申请理由（例如："需要通过API操作多维表数据"）
   - 提交申请后，等待企业管理员审核通过

## 三、获取多维表的App Token

### 新版多维表界面（2024）获取方法

1. **打开飞书多维表**
   - 打开飞书客户端，进入您想要操作的多维表

2. **获取App Token**
   - 点击多维表右上角的**更多**按钮（三个点图标）
   - 在弹出的菜单中，选择**分享**选项
   - 在分享窗口中，点击**高级设置**按钮
   - 在高级设置面板中，找到**应用Token**（即app_token）
   - 点击**复制**按钮保存该Token

### 从URL中获取App Token（适用于新旧版本）

- **标准多维表URL格式**：`https://feishu.cn/base/xxxxxxxxx`
  - 其中 `xxxxxxxxx` 部分即为App Token
- **Wiki类型多维表URL格式**：`https://wye71g7oh1.feishu.cn/wiki/IkjiwdafsdfasfdsafOcZlIXnic?from=from_copylink`
  - 对于wiki类型的多维表链接，App Token通常不会直接显示在URL中
  - 请使用上述通过分享设置获取App Token的方法
  - 注意：URL中的`IkjiwONBuiHEBikQs0OcZlIXnic`是wiki页面ID，不是App Token

## 四、获取多维表的Table ID

### 新版多维表界面（2024）获取方法

1. **打开多维表**
   - 在飞书客户端中打开您的多维表

2. **获取Table ID**
   - 方法一：通过界面操作
     - 点击多维表底部的表名称旁边的**更多**按钮（三个点图标）
     - 选择**表设置**或**查看表结构**选项
     - 在新打开的页面中，查看浏览器地址栏中的URL
     - URL格式通常为：`https://feishu.cn/base/xxxxxxxxx/table/yyyyyyyyy/structure`
     - 其中 `yyyyyyyyy` 部分即为Table ID
   
   - 方法二：通过URL查询参数
     - 对于**Wiki类型多维表链接**，如果URL中包含查询参数`table=tbllKyGtC8BBHRUv`，那么`tbllKyGtC8BBHRUv`就是Table ID
   
   - 方法三：通过API查询
     - 使用我们提供的`query_feishu_sheet_records`函数查询表信息来获取Table ID
     - 示例：先仅传入认证参数，不设置过滤条件，查看返回的表信息

## 五、配置与使用说明

1. **参数填写**
   - 在使用我们提供的飞书多维表工具时，请确保正确填写以下参数：
     - `app_id`: 从开放平台获取的App ID
     - `app_secret`: 从开放平台获取的App Secret
     - `app_token`: 从多维表获取的应用Token
     - `table_id`: 从多维表获取的表ID

2. **安全注意事项**
   - App Secret是非常重要的凭证，请妥善保管，不要泄露给未授权的人员
   - 建议将这些凭证存储在安全的地方，例如环境变量或密码管理系统中
   - 定期更新App Secret以确保安全性

## 六、测试应用权限

1. **使用我们提供的工具进行测试**
   - 您可以使用`query_feishu_sheet_records`函数测试是否能够成功连接到多维表并获取数据
   - 例如：调用该函数，只填写必要的认证参数，不设置过滤条件

2. **常见问题排查**
   - 如果出现权限错误，请检查应用是否已获得相应权限，以及权限是否已被管理员审核通过
   - 如果出现认证错误，请检查App ID和App Secret是否正确
   - 如果出现找不到表或记录的错误，请检查app_token和table_id是否正确

## 七、其他资源

- [飞书开放平台文档](https://open.feishu.cn/document/)
- [多维表API文档](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/bitable-v1/overview)
- [飞书开发者社区](https://open.feishu.cn/community/)

通过以上步骤，您应该能够成功配置飞书应用并获取所有必要的参数来使用我们提供的多维表工具。如果您在配置过程中遇到任何问题，请参考飞书开放平台的官方文档或联系飞书技术支持。
