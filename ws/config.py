# 用于存储每个单片机的录音音频流队列
CONNECTIONS={}
CLIENTS={}
TASKS={}

# =======================================数据库配置=====================================================================

DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/AI_TOY"



#==============================================asr,tts配置===============================================================
APPID = "7852079912"    # 项目的 appid
TOKEN = "QVsAQkV9k72GYRPZ2sQ40D3iE_hUjYJW"    # 项目的 token


#=============================================LLM配置==============================================================
URL='https://api.coze.cn/open_api/v2/chat'
AUTHORIZATION="Bearer pat_OJfFqZIp1K6DSWw95lwwrNjSOGKc6UsYLqjl7t6LnHXTt4xT8KcdF2otjnKn2xhi"































#
# #默认参数
# CONFIG_DICT={
#     "bot_id": "7383896597031485490",#默认孩童陪伴
#     "chat_history": [],
#     "voice_type": "BV064_streaming",  # 音色,默认小萝莉
#     "speed_ratio": 1.0,  # 语速,默认1.0
#     "volume_ratio": 3.0,  # 音量,默认3.0
#     "pitch_ratio": 1.0,  # 音调,默认1.0
# }


# #========================================COZE模型配置=====================================================================
# COZE_HEADERS = {
#     'Content-Type': 'application/json; charset=utf-8',
#     'Authorization': 'Bearer pat_7hvslWGpZGLy3nqH4tUad4ZegGGyc7vNJXORrMxajws262S4QLjffirMIC3NNGYK',
#     'Connection': 'keep-alive',
#     'Accept': '*/*'
# }
# COZE_DATA = {
#     # 'bot_id': '7383896597031485490',#孩童陪伴
#     # 'bot_id':'7390379454117691402',#仙剑奇侠传
#     'bot_id': CONFIG_DICT['bot_id'],#动态bot_id
#     'chat_history': CONFIG_DICT['chat_history'],#动态chat_history
#     'user': 'Alvan',
#     'query': '',
#     'stream': False,
#     # 'conversation_id': self.conversation_id,
# }
# # =======================================语音合成配置======================================================================
# TTS_CONFIG={
#     "voice_type": CONFIG_DICT['voice_type'],
#     "speed_ratio": CONFIG_DICT['speed_ratio'],
#     "volume_ratio": CONFIG_DICT['volume_ratio'],
#     "pitch_ratio": CONFIG_DICT['pitch_ratio']
# }

