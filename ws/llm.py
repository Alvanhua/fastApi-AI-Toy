import asyncio
import json
import ssl

import aiohttp
from .tts import test_submit
from .config import CLIENTS,URL,AUTHORIZATION

# 创建不验证证书的 SSL 上下文
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


url = URL
COZE_HEADERS = {
    'Content-Type': 'application/json; charset=utf-8',
    'Authorization':AUTHORIZATION,
    'Connection': 'keep-alive',
    'Accept': '*/*'
}
COZE_DATA = {
    'bot_id': '7428427454739447845',  # 动态bot_id 孩童陪伴
    'chat_history': [],  # 动态chat_history
    'user': 'Alvan',
    'query': '',
    'stream': True,
}



async def post_request(query,mac_address,get_config,sentence="", all_sentence=""):
    per_config = json.loads(get_config)  # 转为字典
    # 覆盖coze配置
    coze_config = per_config['coze_config']
    # print("扣子配置:",coze_config)
    COZE_DATA['bot_id'] = coze_config['bot_id']
    COZE_DATA['chat_history']=coze_config['chat_history']
    COZE_DATA['query'] = query
    histories=COZE_DATA['chat_history']
    histories.append({
        'role': 'user',
        'content': query,
        'content_type': 'text'
    })


    tts_config = per_config['tts_config']
    # print("TTS配置:",tts_config)
    # 使用自定义的 connector
    connector = aiohttp.TCPConnector(ssl_context=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.post(url, headers=COZE_HEADERS, json=COZE_DATA) as response:
            if response.status == 200:
                # 读取 SSE 流
                count = 1
                async for line in response.content:
                    data = line.decode('utf-8').strip()[5:]
                    if data:
                        # 解码每一行
                        json_data = json.loads(data)
                        event = json_data['event']
                        if event !='done':
                            is_finish=json_data['is_finish']
                        if event == 'message':
                            message = json_data['message']
                            content = message['content']
                            all_sentence += content.split('{')[0]
                            sentence += content.split('{')[0]


                            if content in ['。', '！', '？', '，','.','!','?',','] and len(sentence) >= 6 ** count:
                                # 跑tts纯流式
                                # print(f"第{str(count)}句:",sentence)
                                await test_submit(sentence,mac_address,tts_config)
                                count += 1
                                sentence = ""
                            elif content == '' and len(sentence) < 6 ** count and is_finish and json_data['index']==0:
                                # print(f"最后一句:",sentence)
                                if sentence!='':
                                    await test_submit(sentence,mac_address,tts_config)
                                    sentence = ""

                        elif event == 'done':
                            pass
                            # print("LLM生成结束")
                        elif event == 'error':
                            error_information = json_data['error_information']
                            print(
                                f"chat 错误结束，错误码：{error_information['code']}，错误信息：{error_information['msg']}")
    await CLIENTS[mac_address].send_text("finish_tts")
    # 响应的回来的记录
    assistant_res={
        "role": "assistant",
        "type": "answer",
        "content": all_sentence,
        "content_type": "text"
    }
    histories.append(assistant_res)
    if len(histories)>=20:
        del histories[:2]
    print(f"{mac_address}-答:",all_sentence)
    return per_config










# 运行异步函数
if __name__ == '__main__':
    asyncio.run(post_request())