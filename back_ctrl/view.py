import json

from fastapi import APIRouter, Response, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from ws.db import get_db
from model.model import MAiToy
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates
from ws.db_redis import re

templates = Jinja2Templates(directory="templates")

maitoy = APIRouter()


class UpdateItem(BaseModel):
    mac_addr: str
    bot_id: str
    voice_type: str
    speed_ratio: float
    volume_ratio: float
    pitch_ratio: float


@maitoy.put("/maitoy")
async def update_maitoy(item: UpdateItem):
    db: AsyncSession = await get_db()
    update_data = item.dict(exclude_unset=True)
    print(update_data)

    # 构建查询语句
    stmt = select(MAiToy).where(MAiToy.mac_addr == item.mac_addr)
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()

    if record:
        # 构建更新语句
        stmt = (
            update(MAiToy)
            .where(MAiToy.mac_addr == item.mac_addr)
            .values(**update_data)
        )
        await db.execute(stmt)
        await db.commit()

        # 更新redis
        old_config = await re.get(update_data["mac_addr"])
        if old_config:
            old_config = eval(old_config)  # 将旧的配置从字符串转换为字典
            old_config["coze_config"]["bot_id"] = update_data["bot_id"]
            old_config["tts_config"] = {
                "voice_type": update_data["voice_type"],
                "speed_ratio": update_data["speed_ratio"],
                "volume_ratio": update_data["volume_ratio"],
                "pitch_ratio": update_data["pitch_ratio"]
            }

            await re.set(update_data["mac_addr"], json.dumps(old_config), ex=3600)

        return "修改成功!"
    else:
        return {"message": "Record not found"}


@maitoy.get("/maitoy", response_class=HTMLResponse)
async def get_maitoy(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
