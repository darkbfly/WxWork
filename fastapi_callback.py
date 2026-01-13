#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业微信回调验证接口 - FastAPI 实现
用于验证企业微信回调 URL 的有效性
"""
import sys
import os
import urllib.parse
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import PlainTextResponse
from typing import Optional

# 添加 callback_python3 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'callback_python3'))

from WXBizMsgCrypt import WXBizMsgCrypt
import ierror

app = FastAPI(title="企业微信回调验证接口")

# 配置参数 - 从环境变量或配置文件读取
# 这些参数需要从企业微信后台获取
TOKEN = os.getenv("WXWORK_TOKEN", "your_token_here")
ENCODING_AES_KEY = os.getenv("WXWORK_ENCODING_AES_KEY", "your_encoding_aes_key_here")
CORP_ID = os.getenv("WXWORK_CORP_ID", "your_corp_id_here")


@app.get("/", response_class=PlainTextResponse)
async def verify_callback_url(
    msg_signature: str = Query(..., description="企业微信加密签名"),
    timestamp: str = Query(..., description="时间戳"),
    nonce: str = Query(..., description="随机数"),
    echostr: str = Query(..., description="加密的字符串")
):
    """
    验证企业微信回调 URL 的有效性
    
    企业微信会向此接口发送 GET 请求进行验证：
    GET /?msg_signature=xxx&timestamp=xxx&nonce=xxx&echostr=xxx
    
    返回：
    - 验证成功：返回解密后的明文消息（不能加引号，不能带BOM头，不能带换行符）
    - 验证失败：返回错误信息
    """
    try:
        # 1. 对收到的请求参数做 URL 解码处理
        # FastAPI 会自动进行 URL 解码，但为了确保，我们再次显式解码
        decoded_echostr = urllib.parse.unquote(echostr)
        decoded_msg_signature = urllib.parse.unquote(msg_signature)
        decoded_timestamp = urllib.parse.unquote(timestamp)
        decoded_nonce = urllib.parse.unquote(nonce)
        
        # 2. 初始化加解密对象
        wxcpt = WXBizMsgCrypt(TOKEN, ENCODING_AES_KEY, CORP_ID)
        
        # 3. 验证消息体签名并解密 echostr
        # VerifyURL 方法会：
        #   - 验证消息体签名的正确性
        #   - 解密 echostr 参数得到消息内容（即 msg 字段）
        ret, sEchoStr = wxcpt.VerifyURL(
            decoded_msg_signature,
            decoded_timestamp,
            decoded_nonce,
            decoded_echostr
        )
        
        if ret != ierror.WXBizMsgCrypt_OK:
            # 验证失败，返回错误信息
            error_messages = {
                ierror.WXBizMsgCrypt_ValidateSignature_Error: "签名验证失败",
                ierror.WXBizMsgCrypt_ComputeSignature_Error: "签名计算错误",
                ierror.WXBizMsgCrypt_DecryptAES_Error: "解密失败",
                ierror.WXBizMsgCrypt_IllegalAesKey: "AES密钥非法",
                ierror.WXBizMsgCrypt_ValidateCorpid_Error: "CorpID验证失败",
            }
            error_msg = error_messages.get(ret, f"验证失败，错误码: {ret}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # 4. 验证成功，返回解密后的明文消息内容
        # 注意：不能加引号，不能带BOM头，不能带换行符
        # 确保返回的是纯文本，去除可能的换行符和空白字符
        sEchoStr = sEchoStr.strip() if sEchoStr else ""
        return PlainTextResponse(content=sEchoStr, media_type="text/plain")
        
    except HTTPException:
        raise
    except Exception as e:
        # 处理其他异常
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "message": "服务运行正常"}


if __name__ == "__main__":
    import uvicorn
    
    # 检查配置参数
    if TOKEN == "your_token_here" or ENCODING_AES_KEY == "your_encoding_aes_key_here" or CORP_ID == "your_corp_id_here":
        print("警告: 请设置环境变量或修改代码中的配置参数:")
        print("  - WXWORK_TOKEN: 企业微信后台设置的 Token")
        print("  - WXWORK_ENCODING_AES_KEY: 企业微信后台设置的 EncodingAESKey")
        print("  - WXWORK_CORP_ID: 企业微信的 CorpID")
        print("\n或者直接修改 fastapi_callback.py 文件中的 TOKEN, ENCODING_AES_KEY, CORP_ID 变量")
    
    # 启动服务
    uvicorn.run(app, host="0.0.0.0", port=8000)
