# FastAPI 企业微信回调验证接口使用说明

## 功能说明

本接口实现了企业微信回调 URL 验证功能。当在企业微信后台配置回调 URL 时，企业微信会向该 URL 发送 GET 请求进行验证。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置参数

在运行服务前，需要配置以下三个参数：

1. **Token**: 企业微信后台设置的 Token
2. **EncodingAESKey**: 企业微信后台设置的 EncodingAESKey（43 位字符的 Base64 编码）
3. **CorpID**: 企业微信的 CorpID

### 配置方式

#### 方式一：使用环境变量（推荐）

```bash
# Windows PowerShell
$env:WXWORK_TOKEN="your_token"
$env:WXWORK_ENCODING_AES_KEY="your_encoding_aes_key"
$env:WXWORK_CORP_ID="your_corp_id"

# Linux/Mac
export WXWORK_TOKEN="your_token"
export WXWORK_ENCODING_AES_KEY="your_encoding_aes_key"
export WXWORK_CORP_ID="your_corp_id"
```

#### 方式二：直接修改代码

编辑 `fastapi_callback.py` 文件，修改以下变量：

```python
TOKEN = "your_token_here"
ENCODING_AES_KEY = "your_encoding_aes_key_here"
CORP_ID = "your_corp_id_here"
```

## 启动服务

```bash
python fastapi_callback.py
```

服务默认运行在 `http://0.0.0.0:8000`

### 使用 uvicorn 启动（推荐生产环境）

```bash
uvicorn fastapi_callback:app --host 0.0.0.0 --port 8000
```

## 接口说明

### 验证回调 URL

**请求方式**: GET

**请求地址**: `http://your-domain.com/`

**请求参数**:

| 参数 | 类型 | 必须 | 说明 |
|------|------|------|------|
| msg_signature | string | 是 | 企业微信加密签名 |
| timestamp | string | 是 | 时间戳 |
| nonce | string | 是 | 随机数 |
| echostr | string | 是 | 加密的字符串 |

**请求示例**:

```
GET http://api.3dept.com/?msg_signature=ASDFQWEXZCVAQFASDFASDFSS&timestamp=13500001234&nonce=123412323&echostr=ENCRYPT_STR
```

**响应说明**:

- 验证成功：返回解密后的明文消息内容（纯文本，无引号、无BOM头、无换行符）
- 验证失败：返回 HTTP 400 错误，包含错误信息

### 健康检查

**请求方式**: GET

**请求地址**: `http://your-domain.com/health`

**响应示例**:

```json
{
  "status": "ok",
  "message": "服务运行正常"
}
```

## 验证流程

1. 企业微信向配置的回调 URL 发送 GET 请求
2. 接口接收请求参数（msg_signature, timestamp, nonce, echostr）
3. 对参数进行 URL 解码处理
4. 使用 `WXBizMsgCrypt.VerifyURL` 方法：
   - 验证消息体签名的正确性
   - 解密 echostr 参数得到消息内容明文
5. 在 1 秒内原样返回明文消息内容

## 注意事项

1. **URL 解码**: 接口会自动对接收到的参数进行 URL 解码
2. **响应格式**: 返回的明文消息不能加引号，不能带 BOM 头，不能带换行符
3. **响应时间**: 必须在 1 秒内返回响应
4. **错误处理**: 验证失败时会返回相应的错误信息

## 测试

可以使用企业微信的接口调试工具进行测试：
1. 访问 [企业微信接口调试工具](https://work.weixin.qq.com/api/devtools/devtool.php)
2. 依次选择：建立连接 > 测试回调模式
3. 输入你的回调 URL 和配置参数进行测试

## 常见问题

### 1. 导入错误：No module named 'Crypto'

解决方案：安装 pycryptodome

```bash
pip install pycryptodome
```

### 2. 验证失败：签名验证失败

- 检查 Token 是否正确
- 检查参数是否正确进行了 URL 解码
- 检查时间戳是否在有效期内

### 3. 验证失败：解密失败

- 检查 EncodingAESKey 是否正确（43 位字符的 Base64 编码）
- 检查 CorpID 是否正确

## 相关文档

- [企业微信官方文档 - 回调模式](https://work.weixin.qq.com/api/doc#90000/90135/90930)
- [企业微信接口调试工具](https://work.weixin.qq.com/api/devtools/devtool.php)
