import aioredis
import json
from .db import get_db
from model.model import MAiToy
from sqlalchemy import select

# 创建一个redis实例
re = aioredis.from_url("redis://localhost:6379/5")


# 数据库里取动态参数
async def get_db_config(mac_addr, db):
    # 取数据库里的配置参数
    obj = await db.execute(select(MAiToy).filter(MAiToy.mac_addr == mac_addr))
    obj=obj.scalars().first()

    # 如果没有obj数据, 创建一个新数据
    if not obj:
        new_obj = MAiToy(mac_addr=mac_addr)
        db.add(new_obj)
        await db.commit()
        obj = new_obj

    config_obj = {
        'bot_id': obj.bot_id,
        'voice_type': obj.voice_type,
        'speed_ratio': obj.speed_ratio,
        'volume_ratio': obj.volume_ratio,
        'pitch_ratio': obj.pitch_ratio
    }

    json_data = json.dumps({
        "coze_config": {
            "bot_id": config_obj['bot_id'],
            "chat_history": []
        },
        "tts_config": {
            "voice_type": config_obj['voice_type'],
            "speed_ratio": config_obj['speed_ratio'],
            "volume_ratio": config_obj['volume_ratio'],
            "pitch_ratio": config_obj['pitch_ratio']
        }
    })
    return json_data


# 获取redis配置,如果redis有配置,则取redis配置,如果redis没有配置,则取数据库配置,并且设置redis过期时间为3600秒
async def get_redis_config(mac_addr):
    get_config = await re.get(mac_addr)
    # 取到redis动态参数
    if not get_config:
        # 取数据库动态参数
        db = await get_db()
        get_config = await get_db_config(mac_addr, db)
        # 设置redis的过期时间为3600秒
        await re.set(mac_addr, get_config, ex=3600)
    return get_config
