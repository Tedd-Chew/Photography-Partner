# ====== 光影参谋 后端配置 ======
# 复制此文件为 config.py 并填入实际值

# vivo AI 平台
VIVO_APP_KEY = "your_AppKey"
VIVO_BASE_URL = "https://api-ai.vivo.com.cn/v1"
MODEL_NAME = "Volc-DeepSeek-V3.2"

# 数据库
DB_PATH = "data/app.db"

# 图片
MAX_IMAGE_SIZE = 1024          # 最长边像素
JPEG_QUALITY = 80              # 压缩质量

# 服务器
HOST = "0.0.0.0"
PORT = 8000

# 经验规则
EXP_PER_ANALYSIS = 10          # 每次分析基础经验
EXP_HIGH_SCORE = 15            # >80 分额外经验
EXP_PERFECT_SCORE = 30         # >90 分额外经验
DAILY_ANALYSIS_LIMIT = 5       # 每日经验获取次数上限
