from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from back_ctrl.view import maitoy
from ws.websocket import websocket_endpoint

app = FastAPI()
# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


app.add_websocket_route("/", websocket_endpoint)
app.include_router(maitoy)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)









