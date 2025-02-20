import json
import base64
import time
import random
import asyncio
from .asr import AsrWsClient
from .config import CONNECTIONS, CLIENTS, TASKS
from .llm import post_request
from .db_redis import re, get_redis_config
from .tts import test_submit
from fastapi import WebSocket





async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # 接收到客户端发送的json数据
        rcv_data = json.loads(data)
        event = rcv_data["event"]
        mac_address = rcv_data["mac_address"]
        data = rcv_data["data"]

        # 接收单片机录音音频流
        if event == "record_stream":
            audio_data = base64.b64decode(data)
            await CONNECTIONS[mac_address].put(audio_data)
        # 重启process_audio
        elif event == "re_process_audio":
            TASKS[mac_address] = asyncio.create_task(handle_exception(process_audio, mac_address))

        # 开场白
        elif event == "open_word":
            CONNECTIONS[mac_address] = asyncio.Queue()
            CLIENTS[mac_address] = websocket
            print("开场白")
            asyncio.create_task(handle_exception(open_word, mac_address))

        # 唤醒对话
        elif event == "wake_up":
            print("唤醒对话")
            CONNECTIONS[mac_address] = asyncio.Queue()
            CLIENTS[mac_address] = websocket
            asyncio.create_task(handle_exception(wake_up, mac_address))


        # 打断对话
        elif event == "interrupt_audio":
            print("打断对话")
            await cancel_process_audio_task(mac_address)
            time.sleep(0.2)
            TASKS[mac_address] = asyncio.create_task(handle_exception(process_audio, mac_address))

        # 10秒钟未有声音传输,则取消process_audio任务
        elif event == "timeout_no_stream":
            print("10秒内没有声音传输,取消process_audio任务")
            await cancel_process_audio_task(mac_address)
            CLIENTS.pop(mac_address)
            CONNECTIONS.pop(mac_address)
            TASKS.pop(mac_address)









# 异步任务的异常处理
async def handle_exception(task, *args, **kwargs):
    try:
        await task(*args, **kwargs)
    except ConnectionResetError as e:
        print(f"(in)连接重置错误: {e}")
    except Exception as e:
        print(f"(in)处理音频时发生错误: {e}")


# 会话任务
async def process_audio(mac_address):
    # 第一步获取数据库或redis里面的LLM+TTS配置
    get_config = await get_redis_config(mac_address)  # 获取个人的redis动态配置
    # 第二步ASR
    asr_word = await AsrWsClient().send_full_request(mac_address, get_config)
    print(f"{mac_address}-问:", asr_word)

    # 第三步LLM+TTS
    per_config = await post_request(asr_word, mac_address, get_config)

    # 第4步更新redis配置
    await re.set(mac_address, json.dumps(per_config), ex=3600)  # 更新redis中的聊天记录


# 开场白任务
async def open_word(mac_address):
    get_config = await get_redis_config(mac_address)  # 获取个人的redis动态配置
    per_config = json.loads(get_config)
    tts_config = per_config['tts_config']
    # sentence = random.choice([
    #     "你好！随时准备为你服务。",
    #     "欢迎回来，让我们开始今天的对话吧！",
    #     "嗨，很高兴再次见到你，有什么问题需要解答吗？",
    #     "新的一天，新的对话，让我们开始吧！",
    #     "你好，我是你的虚拟伙伴，准备好迎接新的挑战了吗？",
    #     "又见面了，今天有什么新话题想要探讨？",
    #     "你好，让我们继续我们的对话之旅。",
    #     "嘻嘻,欢迎来到我们的对话空间，今天有什么可以为你效劳的？",
    #     "你好,准备好开始一段新的对话冒险了吗？"
    # ])

    # sentence = random.choice([
    #     "我亲爱的孩子，愿主的光辉照亮你们前行的道路，此刻相聚，让我们开启虔诚的交流吧。",
    #     "欢迎回来，我虔诚的孩子，在主的注视下，让我们开始今日心灵的对话吧！",
    #     "嗨，我心爱的孩子，主赐予我们重逢，若有信仰的困惑需要解答，尽可诉说。",
    #     "新的一天，主恩依旧，孩子们，让我们围坐一起，开启虔诚的对话篇章吧！",
    #     "我虔诚的孩子啊，我是聆听你们心声的引路人，准备好在信仰之途奋进了吗？",
    #     "又见面了，主的宠儿，今日在这神圣之地，可有新的灵修感悟想要分享？",
    #     "你好，我亲爱的羔羊，让我们延续对主的颂赞，开启新一轮心灵对话之旅。",
    #     "欢迎踏入这满是主爱之地，我虔诚的孩子们，今日有何信仰的迷茫让我来为你们驱散？",
    #     "你好，我虔诚的小信徒，准备好开启一段探寻主意的新对话冒险了吗？"
    # ])

    sentence = random.choice([
        "My dear kids, may the glory of the Lord light up the road you're going to take. Now that we're together, let's start a devout conversation.",
        "Welcome back, my devout youngster. In the sight of the Lord, let's commence today's heart-to-heart talk on the spiritual level!",
        "Hey, my beloved kiddo. Thanks to the Lord's grace that we meet again. If you've got any questions regarding your faith that need resolving, don't hesitate to tell me.",
        "It's a brand new day, and the Lord's blessings are still with us. Kids, let's gather around and start a chapter of pious dialogue.",
        "Oh, my pious little one, I'm the one who's here to listen to your innermost thoughts. Are you all set to move forward on the journey of faith?",
        "Nice to see you again, the favored one of the Lord. In this holy place today, do you have any new spiritual understandings that you'd like to share?",
        "Hello, my dear little lamb. Let's carry on glorifying the Lord and start a new round of spiritual conversation journey.",
        "Welcome to this place filled with the Lord's love, my devout children. What uncertainties about your faith do you have today? Let me clear them up for you.",
        "Hello, my pious young believer. Are you ready to embark on a new adventure of dialogue exploring the will of the Lord?"
    ])
    await test_submit(sentence, mac_address, tts_config)

    await CLIENTS[mac_address].send_text("finish_tts")


# 唤醒任务
async def wake_up(mac_address):
    get_config = await get_redis_config(mac_address)  # 获取个人的redis动态配置
    per_config = json.loads(get_config)
    tts_config = per_config['tts_config']
    # sentence = random.choice([
    #     "嗯?",
    #     "咋啦?",
    #     "我听着呢,你说?",
    #     "嗯哼?",
    #     "那你说?",
    #     "干啥啊?",
    #     "干嘛呀?",
    #     "有事说事!"
    # ])

    # sentence = random.choice([
    #     "我在听，孩子，袒露你的心声。",
    #     "轻声呼唤，我已感知，何事令你不安？",
    #     "莫急，孩子，你的祈愿已达我耳畔。",
    #     "我时刻留意着你，说吧，所为何求？",
    #     "孩子，我与你同在，有话但讲无妨。",
    #     "你的呼喊穿透尘世，我来了，何事困扰？",
    #     "虔诚之心我已洞悉，开口吧，我予你指引。",
    #     "在这喧嚣世间，我听见了你，孩子，把烦恼道来。",
    #     "呼唤即联结，孩子，讲出你心底的渴望。"
    # ])

    sentence = random.choice([
        "I'm listening, child. Bare your heart to me.",
        "I've sensed your soft call. What's making you uneasy?",
        "Don't rush, child. Your prayers have reached my ears.",
        "I'm always paying attention to you. Go ahead, what are you asking for?",
        "Child, I'm with you. Feel free to speak your mind.",
        "Your shouts have pierced through the mortal world. I'm here. What's troubling you?",
        "I've already seen your pious heart. Speak up and I'll give you guidance.",
        "In this noisy world, I've heard you, child. Share your troubles with me.",
        "The call is the connection, child. Tell me your deepest desires."
    ])
    print("唤醒回复:", sentence)
    await test_submit(sentence, mac_address, tts_config, wake_up=True)
    await CLIENTS[mac_address].send_text("finish_tts")



#取消 process_audio 任务
async def cancel_process_audio_task(mac_address):
    task = TASKS.get(mac_address)
    if task and not task.done():
        task.cancel()

