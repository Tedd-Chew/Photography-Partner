# 光影参谋 — 项目架构书

> 一站式 AI 摄影构图成长伴侣 | 快应用 | 2026-05

---

## 技术选型

| 层 | 选择 | 理由 |
|----|------|------|
| 前端 | **快应用 (Quick App / hap)** | 比赛平台要求 |
| 后端 | **Python + FastAPI** | 轻量异步、AI 生态好、几百行代码搞定全部后端 |
| AI 引擎 | **DeepSeek Vision API**（初赛）→ **BlueLM-2.5-3B 端侧**（复赛） | 初赛务实优先，复赛利用主办方端侧模型加分 |
| 存储 | **SQLite** + 文件系统 | 零配置、单文件、无需额外数据库服务 |
| 部署 | 单 VPS / `uvicorn` 一条命令 | 比赛场景追求简单 |

### 为什么不用 Java

后端本质是 **API 代理 + 图片预处理 + 简单 CRUD**，不需要 Spring Boot。Python FastAPI 几百行完成，Java 要几倍代码量，比赛时间紧。

---

## 三大核心功能

```
┌─────────────────────────────────────────────────────────┐
│                    光影参谋 核心功能                       │
├───────────────────┬───────────────────┬─────────────────┤
│ ① 实时拍摄指导     │ ② 后期修图建议     │ ③ 成片评价体系    │
│  (Camera 页)      │  (Analysis 页)    │ (Analysis       │
│                   │                   │  + Growth 页)   │
├───────────────────┼───────────────────┼─────────────────┤
│ • 快应用内置相机    │ • 上传照片         │ • 五维评分        │
│ • 实时预览画面      │ • AI 诊断问题      │   构图/曝光/色彩  │
│ • 构图参考线叠加    │ • 调色建议         │   /清晰度/创意   │
│ • 场景自动识别      │ • 修图步骤教程      │ • 优缺点文字评价   │
│ • 参数实时推荐      │ • 一键跳转修图App   │ • 等级成长体系    │
│   快门/ISO/白平衡   │                   │ • 勋章收集       │
│                   │                   │ • 历史评分趋势    │
└───────────────────┴───────────────────┴─────────────────┘
```

---

## 整体架构

```
┌─────────────────────────┐        HTTP/JSON       ┌──────────────────────────┐
│      快应用前端           │ ────────────────────▶ │     Python 后端           │
│    (Quick App)          │ ◀────────────────────  │   (FastAPI + uvicorn)    │
│                         │                       │                          │
│  ① Camera  拍照指导      │                       │  POST /api/scene/detect  │
│  ② Analysis 修图建议     │ ─ 上传照片 ────────▶ │  POST /api/analyze       │
│  ③ Growth   成长体系     │                       │  GET  /api/user/info     │
│     Gallery  历史画廊     │                       │  POST /api/user/checkin  │
│                         │                       │  GET  /api/gallery       │
└─────────────────────────┘                       └──────────┬───────────────┘
                                                              │
                                                      HTTPS   │
                                                              ▼
                                                    ┌──────────────────┐
                                                    │ DeepSeek Vision  │
                                                    │     API          │
                                                    └──────────────────┘
```

---

## 数据库设计

### SQLite 表结构（3 张表）

用户以**设备 ID** 标识，不需要登录系统。

```sql
-- 用户表
CREATE TABLE users (
    uid TEXT PRIMARY KEY,              -- 设备 ID
    nickname TEXT DEFAULT '',
    level INTEGER DEFAULT 1,           -- 等级 1-6
    exp INTEGER DEFAULT 0,             -- 总经验值
    badges_json TEXT DEFAULT '[]',     -- JSON: ["夜景猎手","构图大师"]
    streak INTEGER DEFAULT 0,          -- 连续打卡天数
    last_checkin TEXT,                 -- 最后打卡日期
    total_analyses INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 分析记录表
CREATE TABLE analyses (
    id TEXT PRIMARY KEY,               -- UUID
    uid TEXT NOT NULL,
    overall_score INTEGER,
    scores_json TEXT,                  -- 五维评分 JSON
    summary TEXT,                      -- AI 总评文字
    strengths_json TEXT,
    weaknesses_json TEXT,
    suggestions_json TEXT,             -- 修图建议 JSON
    tutorial_steps_json TEXT,
    scene_label TEXT,                  -- 场景类型
    image_path TEXT,                   -- 原图路径
    thumb_path TEXT,                   -- 缩略图路径
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (uid) REFERENCES users(uid)
);

-- 打卡记录表
CREATE TABLE checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT NOT NULL,
    date TEXT NOT NULL,
    exp_gained INTEGER DEFAULT 0,
    FOREIGN KEY (uid) REFERENCES users(uid),
    UNIQUE(uid, date)
);
```

---

## 前端 — 快应用

### 目录结构

```
project-root/
├── sign/debug/
├── src/
│   ├── app.ux                     # 应用入口
│   ├── manifest.json              # 路由 + 权限声明
│   │
│   ├── Home/
│   │   └── index.ux               # 首页：三大功能入口 + 成长概览
│   │
│   ├── Camera/
│   │   └── index.ux               # ① 相机 + 参数面板 + 构图线
│   │
│   ├── Analysis/
│   │   └── index.ux               # ②③ 雷达图 + 修图建议 + 评分
│   │
│   ├── Growth/
│   │   └── index.ux               # ③ 等级 + 勋章墙 + 趋势
│   │
│   ├── Gallery/
│   │   └── index.ux               # 历史记录列表
│   │
│   ├── Common/
│   │   ├── ScoreRadar.ux           # 五维雷达图组件
│   │   ├── CompositionLines.ux     # 构图参考线叠加
│   │   ├── ParamPanel.ux           # 参数推荐面板
│   │   ├── PhotoCard.ux            # 照片卡片
│   │   └── LevelBadge.ux           # 等级勋章组件
│   │
│   ├── store/
│   │   └── index.js               # qa-vuex 全局状态
│   │
│   ├── services/
│   │   └── api.js                 # 后端 API 调用封装
│   │
│   └── helper/
│       ├── image.js               # 图片压缩处理
│       └── storage.js             # 本地缓存
│
├── package.json
└── quickapp.config.js
```

### manifest.json

```json
{
  "router": {
    "entry": "Home",
    "pages": {
      "Home":     { "component": "index" },
      "Camera":   { "component": "index" },
      "Analysis": { "component": "index" },
      "Growth":   { "component": "index" },
      "Gallery":  { "component": "index" }
    }
  },
  "features": [
    { "name": "system.media" },
    { "name": "system.fetch" },
    { "name": "system.storage" },
    { "name": "system.device" },
    { "name": "system.sensor" }
  ],
  "permissionDesc": [
    { "name": "CAMERA", "desc": "用于实时取景拍摄与AI分析" },
    { "name": "WRITE_EXTERNAL_STORAGE", "desc": "用于保存分析结果图片" }
  ]
}
```

### 状态管理（qa-vuex Store）

```javascript
// src/store/index.js
{
  state: {
    user: {
      uid: '',
      level: 1,
      exp: 0,
      badges: [],
      streak: 0,
    },
    camera: {
      scene: null,           // { label: '夜景', confidence: 0.9 }
      gridMode: 'thirds',   // 'off' | 'thirds' | 'golden' | 'crosshair'
      params: {
        shutter: null,      // '1/250'
        iso: null,          // '200'
        wb: null,           // '5500K'
      }
    },
    analysis: null,          // 当前分析结果
    history: [],
  }
}
```

---

## 功能 ①：实时拍摄指导（Camera 页）

### 页面布局

```
┌─────────────────────────────┐
│  ← 返回       场景: 🌙 夜景  │
├─────────────────────────────┤
│ ╔═══════════════════════╗   │
│ ║ ┊     ┊     ┊        ║   │
│ ║ ┊──┼──┼──┊        ║   │  ← CSS 实现的构图参考线
│ ║ ┊  │  │  ┊        ║   │    叠加在相机预览上方
│ ║ ┊──┼──┼──┊        ║   │
│ ║ ┊     ┊     ┊        ║   │
│ ╚═══════════════════════╝   │
│        相机实时预览           │  ← 快应用内置 camera
├─────────────────────────────┤
│ 📷 建议参数                   │
│ 快门速度    1/30s            │
│ ISO感光度   800              │
│ 白平衡      4000K (暖色)      │
│ 曝光补偿     +0.3EV          │
├─────────────────────────────┤
│  [ 切换构图线: 三分法 ▾ ]     │
│  [     📸 拍照     ]         │
└─────────────────────────────┘
```

### 场景识别触发机制：按需触发，不做轮询

**为什么不用轮询**：DeepSeek API 按 token 计费，3 秒轮询一次 = 每分钟 20 次调用，烧钱且无意义（用户场景不会频繁变化）。API 往返 1-2 秒，轮询返回时参数可能已过时。

**触发策略：**

```
进入 Camera 页 → 首次自动检测（1 次）
用户手动切换场景类型 → 重新检测
用户点击「刷新参数」按钮 → 重新检测
用户拍照后 → 跳转 Analysis 做深度分析（不同接口）
```

一次拍摄会话只需 **1-2 次** 场景检测调用，深度分析在拍照后单独触发。

前端逻辑：

```javascript
// Camera 页
onReady() {
  this.detectScene()  // ① 首次自动检测，仅一次
},

// 场景切换（用户手动选择: 自动/人像/夜景/风景/美食）
onSceneChange(newScene) {
  if (newScene === 'auto') {
    this.detectScene()  // 切回自动时重新检测
  } else {
    this.scene = newScene  // 手动模式直接用，不调 API
    this.loadPresetParams(newScene)  // 加载预设参数
  }
},

// 手动刷新按钮
onRefreshParams() {
  this.detectScene()
}
```

### 数据流

```
① 进入 Camera 页 → 内置相机启动 + 首次自动检测场景
② 后端 → DeepSeek → 返回 { scene, confidence, params }
③ 前端展示场景标签 + 参数面板
④ 构图参考线默认开启（三分法）
⑤ 用户取景 → 可手动切换场景类型 / 切换构图线 / 刷新参数
⑥ 拍照 → 图片保存 → 可跳转 Analysis 做深度分析
```

### 构图参考线模式

| 模式 | 说明 |
|------|------|
| `off` | 纯净取景，无参考线 |
| `thirds` | 三分法网格（默认） |
| `golden` | 黄金分割线 |
| `crosshair` | 十字中心线 |

---

## 功能 ②：后期修图建议（Analysis 页上半）

### 修图建议展示

```
┌─────────────────────────────┐
│  ← 返回      分析结果        │
├─────────────────────────────┤
│        [照片缩略图]          │
├─────────────────────────────┤
│  🔧 修图建议                  │
│                             │
│  ⚠️ 曝光不足                 │
│  └ 建议：增加曝光 +0.5EV      │
│     [查看修图步骤 ▼]          │
│                             │
│  ⚠️ 色温偏冷                 │
│  └ 建议：白平衡调至 5500K     │
│     [查看修图步骤 ▼]          │
│                             │
│  ✅ 清晰度良好                │
│                             │
│  📱 一键跳转修图              │
│  [Lightroom] [美图秀秀]      │
└─────────────────────────────┘
```

### DeepSeek 调用

```python
# server/services/deepseek.py
ANALYZE_PROMPT = """你是一位专业摄影后期导师。分析这张照片的后期处理问题，返回严格 JSON：

{
  "issues": [
    {
      "category": "曝光/色彩/构图/清晰度/白平衡/对比度/饱和度",
      "severity": "high/medium/low",
      "description": "具体问题描述，20字以内",
      "suggestion": "具体修图建议，30字以内",
      "tutorial_steps": ["步骤1", "步骤2", "步骤3"]
    }
  ],
  "scores": {
    "composition": 0-100,
    "exposure": 0-100,
    "color": 0-100,
    "sharpness": 0-100,
    "creativity": 0-100
  },
  "summary": "总体评价，50字以内",
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["问题1", "问题2"]
}

规则：
1. 只列出确实存在的问题，不要虚构
2. 修图步骤要具体可操作，零基础用户也能看懂
3. 只返回 JSON，不要任何其他文字。"""
```

---

## 功能 ③：成片评价及评分体系

### 五维评分模型

| 维度 | 权重 | 评估内容 |
|------|------|----------|
| 构图 | 30% | 主体位置、画面平衡、三分法、引导线 |
| 曝光 | 25% | 明暗均衡、高光保留、阴影细节 |
| 色彩 | 20% | 白平衡、色彩和谐、饱和度 |
| 清晰度 | 15% | 对焦准确度、细节保留、噪点控制 |
| 创意 | 10% | 视角独特性、表现力、故事感 |

**综合分** = 构图×0.3 + 曝光×0.25 + 色彩×0.2 + 清晰度×0.15 + 创意×0.1

### 等级体系（6 级）

| 等级 | 称号 | 所需经验 | 解锁 |
|------|------|----------|------|
| Lv.1 | 摄影新手 | 0 | 基础功能 |
| Lv.2 | 摄影学徒 | 100 | 解锁全部构图线模式 |
| Lv.3 | 摄影达人 | 300 | 解锁高级参数推荐 |
| Lv.4 | 摄影专家 | 600 | 解锁详细修图教程 |
| Lv.5 | 摄影大师 | 1000 | 解锁风格推荐 |
| Lv.6 | 光影艺术家 | 1600 | 专属勋章 |

### 经验获取

- 每次分析照片：+10 EXP（每日上限 5 次）
- 获得高分（>80分）：额外 +15 EXP
- 获得超高分（>90分）：额外 +30 EXP
- 每日打卡：+5 EXP（连续打卡递增 +5/+8/+10/+12/+15）

### 勋章体系

| 勋章 | 条件 |
|------|------|
| 🌙 夜景猎手 | 拍摄 10 张夜景照片 |
| 👤 人像专家 | 人像评分 >85 累计 5 次 |
| 🍜 美食探索者 | 拍摄 10 张美食照片 |
| 📐 构图大师 | 构图评分 >90 累计 5 次 |
| 🔥 七日坚持 | 连续打卡 7 天 |
| 🏆 首战告捷 | 首次获得 90+ 评分 |
| 🎨 色彩诗人 | 色彩评分 >90 累计 3 次 |
| ⚡ 快速成长 | 3 天内升到 Lv.3 |

### Growth 页展示

```
┌─────────────────────────────┐
│  👤 我的摄影成长              │
├─────────────────────────────┤
│  Lv.3 摄影达人               │
│  ████████████░░░░  420/600  │
│                             │
│  🏅 勋章 (4/8)               │
│  [🌙] [👤] [📐] [🔥]        │
│                             │
│  📈 评分趋势（近7天）          │
│  80│     ╭─╮                │
│  70│ ╭─╯  ╰─╮               │
│  60│╮        ╰─              │
│    └────────────────        │
│    5/7  5/9  5/11 5/13       │
│                             │
│  📊 统计                     │
│  累计分析 23 次  |  平均分 76.5│
│  最高分 92      |  连续打卡 5天│
└─────────────────────────────┘
```

---

## 后端 API

### 接口清单

| 方法 | 端点 | 说明 | 关联功能 |
|------|------|------|----------|
| POST | `/api/scene/detect` | 场景识别 + 参数推荐 | ① 实时拍摄 |
| POST | `/api/analyze` | 照片综合分析（修图建议+评分） | ②③ 修图+评分 |
| GET | `/api/user/info?uid=x` | 获取用户信息 | ③ 成长体系 |
| POST | `/api/user/checkin` | 每日打卡 | ③ 成长体系 |
| GET | `/api/gallery?uid=x` | 历史分析记录列表 | 记录回看 |
| GET | `/api/gallery/:id` | 单条分析详情 | 记录回看 |

### 核心接口合约

**POST /api/analyze**

```
请求: multipart/form-data
  image: <file>           # 照片（必填）
  scene_type: string      # 可选

响应:
{
  "id": "a1b2c3",
  "scores": {
    "composition": 85,
    "exposure": 72,
    "color": 80,
    "sharpness": 90,
    "creativity": 65
  },
  "overall": 78,
  "summary": "这张人像构图遵循三分法，人物清晰，但背景过曝...",
  "strengths": ["人物主体位于三分线交点", "对焦准确"],
  "weaknesses": ["背景天空过曝", "色温偏冷"],
  "suggestions": [
    { "category": "曝光", "tip": "降低0.3EV曝光补偿" },
    { "category": "色彩", "tip": "白平衡调至5500K" }
  ],
  "tutorial_steps": [
    "打开修图App → 亮度 → 降低曝光10-15",
    "颜色 → 色温 → 右移至5500K"
  ],
  "scene": { "label": "人像", "confidence": 0.92 },
  "exp_gained": 25,
  "badge_unlocked": null,
  "timestamp": "2026-05-13T12:00:00Z"
}
```

**POST /api/scene/detect**

```
请求: multipart/form-data
  image: <file>           # 低分辨率预览帧

响应:
{
  "scene": "夜景",
  "confidence": 0.87,
  "suggested_params": {
    "shutter": "1/30",
    "iso": "800",
    "wb": "4000K"
  }
}
```

### 后端目录结构

```
server/
├── main.py                 # FastAPI 入口
├── config.py               # 配置（API Key、数据库路径等）
├── requirements.txt        # 依赖
│
├── routes/
│   ├── analyze.py          # POST /api/analyze（核心）
│   ├── scene.py            # POST /api/scene/detect
│   ├── user.py             # 用户相关接口
│   └── gallery.py          # 历史记录接口
│
├── services/
│   ├── deepseek.py         # DeepSeek Vision API 封装
│   ├── scoring.py          # 评分计算与标准化
│   └── composition.py      # 本地构图规则引擎
│
├── models/
│   └── database.py         # SQLite 连接 + 表初始化
│
├── prompts/
│   ├── analyze.txt         # 修图+评分 prompt
│   └── scene.txt           # 场景识别 prompt
│
├── utils/
│   ├── image.py             # 图片压缩、转 base64
│   └── response.py          # 统一响应格式
│
├── data/                    # SQLite 文件（自动生成）
└── static/                  # 照片缩略图存储
```

### requirements.txt

```
fastapi==0.115.*
uvicorn==0.34.*
python-multipart==0.0.*
httpx==0.28.*
Pillow==11.*
aiosqlite==0.20.*
pydantic==2.*
```

### main.py

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import analyze, scene, user, gallery
from models.database import init_db

app = FastAPI(title="光影参谋 API")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(analyze.router)
app.include_router(scene.router)
app.include_router(user.router)
app.include_router(gallery.router)

@app.on_event("startup")
async def startup():
    await init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 用户操作流程

```
              首次使用 → 获取设备ID → 后端初始化用户
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌──────────────────┐            ┌──────────────────┐
    │ ① 实时拍摄指导     │            │ ② 上传已有照片     │
    │                  │            │                  │
    │ Camera 页        │            │ 首页点击「选图分析」 │
    │ 取景→场景识别→参数 │            │ 选照片→压缩→上传    │
    │ →构图线→拍照      │            │                  │
    └────────┬─────────┘            └────────┬─────────┘
             │                               │
             └───────────┬───────────────────┘
                         ▼
              ┌──────────────────┐
              │ POST /api/analyze │
              │ 图片 → DeepSeek    │
              └────────┬─────────┘
                       ▼
              ┌──────────────────┐
              │  ③ 结果展示       │
              │                  │
              │  五维雷达图        │
              │  修图建议 + 步骤   │
              │  优缺点评价        │
              │  经验加成提示      │
              │  勋章获得提示      │
              └────────┬─────────┘
                       ▼
              ┌──────────────────┐
              │  Growth 页        │
              │  等级进度         │
              │  勋章收集         │
              │  评分趋势         │
              │  每日打卡         │
              └──────────────────┘
```

---

## 开发阶段

### Phase 1：骨架搭建
- 初始化快应用项目（`hap init`）
- Python FastAPI 后端骨架 + SQLite 初始化
- 申请 DeepSeek API Key + 验证连通性
- 5 个页面基础路由 + 6 个接口骨架

### Phase 2：功能 ① 实时拍摄指导
- Camera 页：快应用内置相机接入
- 构图参考线组件（CSS overlay）
- 参数推荐面板 UI
- `POST /api/scene/detect` 实现
- 场景识别 prompt 调优

### Phase 3：功能 ②③ 修图建议 + 评分
- Analysis 页完整 UI
- ScoreRadar 五维雷达图组件
- `POST /api/analyze` 完整实现
- DeepSeek prompt 调优
- 本地构图规则引擎
- 用户表 + 分析记录表 CRUD

### Phase 4：成长体系
- Growth 页：等级进度 + 勋章墙 + 趋势
- 经验计算与升级逻辑
- 勋章判定逻辑
- 每日打卡功能

### Phase 5：UI 打磨 + 联调
- 整体 UI/UX 优化
- 图片压缩策略调优
- 异常处理（网络超时、AI 解析失败）
- 本地缓存离线查看历史
- 端到端测试

---

## 风险与应对

| 风险 | 应对 |
|------|------|
| DeepSeek API 不稳定 | 超时 30s + 重试 + 友好错误提示 |
| 快应用相机 API 受限 | 降级：调用系统相机 → 返回后选图分析 |
| AI 返回 JSON 不规整 | Prompt 强约束 + 正则兜底解析 |
| 2MB 包体积超限 | 图片外置、CSS 精简、组件复用 |
| 拍照→分析延迟大 | 图片压缩至 1024px + loading 进度 |

---

## 团队分工（4 人）

### 架构分层与人员对应

```
┌──────────────────────────────────────────────────────┐
│                    快应用前端                          │
│  ┌──────────────┐  ┌──────────────┐                  │
│  │  页面逻辑      │  │  UI 组件      │                 │
│  │  Store/路由   │  │  样式/交互    │                 │
│  │  API 调用     │  │              │                 │
│  │  前端同学      │  │  UI 同学      │                │
│  └──────┬───────┘  └──────────────┘                  │
│         │              │                              │
│         │    props     │                              │
│         └──────┬───────┘                              │
│                │                                       │
└────────────────┼───────────────────────────────────────┘
                 │  HTTP (JSON)
┌────────────────┼───────────────────────────────────────┐
│                ▼                Python 后端              │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │  传统后端         │  │  AI 服务         │             │
│  │  routes/        │  │  services/      │              │
│  │  models/        │◀─┤  deepseek.py    │              │
│  │  utils/         │  │  scoring.py     │              │
│  │  你（后端）       │  │  composition.py │              │
│  └────────┬────────┘  │  prompts/       │              │
│           │           │  AI 同学         │              │
│           │  函数调用   └─────────────────┘              │
│           ▼                                            │
│  from services.deepseek import analyze_photo           │
│  result = await analyze_photo(img_b64)                 │
└────────────────────────────────────────────────────────┘
```

### 四人分工

| 角色 | 谁 | 负责 | 关键文件 |
|------|-----|------|----------|
| **传统后端** | 你 | 路由层、数据库 CRUD、图片处理、用户系统、画廊、打卡 | `routes/` `models/` `utils/` `main.py` `config.py` |
| **AI 服务** | 成员 2 | DeepSeek API 封装、Prompt 工程、评分计算、构图规则引擎 | `services/deepseek.py` `services/scoring.py` `services/composition.py` `prompts/` |
| **快应用前端** | 成员 3 | 5 页面逻辑、qa-vuex Store、路由配置、API 调用、相机接入 | `src/pages/*` `src/store/` `src/services/api.js` `manifest.json` |
| **UI + 产品** | 成员 4 | 共享组件库（5 个组件）、页面样式规范、Prompt 迭代测试、端到端测试、答辩材料 | `src/Common/*` `prompts/` 测试脚本 |

---

## 传统后端 — 你的职责

### 你需要创建的文件

```
server/
├── main.py                 # FastAPI 入口，注册路由，挂载静态文件
├── config.py               # 数据库路径、DeepSeek API Key、端口等配置
│
├── routes/                 # ★ 路由层：接收请求 → 调 AI 服务 → 操作数据库 → 返回响应
│   ├── analyze.py          # POST /api/analyze     核心：接收图片，调 AI，存记录，返结果
│   ├── scene.py            # POST /api/scene/detect 场景识别 + 参数推荐
│   ├── user.py             # GET /api/user/info + POST /api/user/checkin
│   └── gallery.py          # GET /api/gallery + GET /api/gallery/:id
│
├── models/
│   └── database.py         # ★ SQLite 连接、建表、插入、查询、更新
│
├── utils/
│   ├── image.py             # ★ 图片工具：打开上传文件、压缩至 1024px、转 base64
│   └── response.py          # 统一响应格式：{ ok: true, data: {...} } 或 { ok: false, error: "..." }
│
└── data/                    # SQLite 文件（自动生成，不用手动创建）
```

### 你需要实现的 6 个接口

#### 1. `POST /api/analyze` — 最核心

```
输入: multipart/form-data { image: File, scene_type?: string }

你的处理流程:
  ① 从 UploadFile 读取图片 bytes
  ② 调 utils/image.py → compress_to_1024() → to_base64()
  ③ 调 AI 同学的服务:  from services.deepseek import analyze_photo
     result = await analyze_photo(image_base64)
  ④ 存数据库: INSERT INTO analyses (...)
  ⑤ 更新用户经验: UPDATE users SET exp = exp + ?, total_analyses += 1
  ⑥ 检查升级/勋章
  ⑦ 返回完整结果给前端

响应: { id, scores, overall, summary, strengths, weaknesses, 
        suggestions, tutorial_steps, scene, exp_gained, badge_unlocked, timestamp }
```

#### 2. `POST /api/scene/detect`

```
输入: multipart/form-data { image: File }

你的处理流程:
  ① 压缩图片（小图即可，功耗低）
  ② to_base64()
  ③ 调 AI 同学:  from services.deepseek import detect_scene
     result = await detect_scene(image_base64)
  ④ 直接返回，不需要存库

响应: { scene, confidence, suggested_params: { shutter, iso, wb } }
```

#### 3. `GET /api/user/info?uid=xxx`

```
处理流程:
  ① 查 users 表
  ② 有记录 → 返回
  ③ 无记录 → INSERT 新用户 (level=1, exp=0) → 返回

响应: { uid, level, exp, badges, streak, total_analyses, last_checkin }
```

#### 4. `POST /api/user/checkin`

```
输入: { uid: string }

处理流程:
  ① 查 users 表 last_checkin
  ② 判断:
     - 今天已打卡 → 返回 { already_checked: true }
     - 昨天打过 → streak += 1，exp += (5 + streak * 2)
     - 断签 → streak = 1，exp += 5
  ③ INSERT checkins 表
  ④ UPDATE users
  ⑤ 检查升级

响应: { streak, exp_gained, level_up: false }
```

#### 5. `GET /api/gallery?uid=xxx&page=1&size=20`

```
处理流程:
  ① 查 analyses 表 WHERE uid=? ORDER BY created_at DESC
  ② 分页返回

响应: { items: [{ id, overall, scene, thumb_url, created_at }], total, page }
```

#### 6. `GET /api/gallery/:id`

```
处理流程:
  ① 查 analyses 表 WHERE id=?

响应: 单条完整分析记录（同 POST /api/analyze 的响应格式）
```

### 数据库操作函数参考（models/database.py）

```python
import aiosqlite
import json

DB_PATH = "data/app.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute("""CREATE TABLE IF NOT EXISTS users (...)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS analyses (...)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS checkins (...)""")
        await db.commit()

# 你需要实现的函数（示例签名）:

async def get_or_create_user(uid: str) -> dict:
    """查用户，不存在则创建新用户并返回"""

async def update_user_exp(uid: str, exp_delta: int) -> dict:
    """增加经验，检查升级，返回 { level_up: bool, new_level: int }"""

async def save_analysis(data: dict) -> str:
    """保存分析记录，返回记录 id"""

async def get_analyses(uid: str, page: int, size: int) -> dict:
    """分页查询历史记录"""

async def get_analysis_by_id(id: str) -> dict:
    """单条记录详情"""

async def do_checkin(uid: str) -> dict:
    """打卡逻辑，返回 { streak, exp_gained, level_up }"""
```

### 注意事项

1. **图片处理先做**：`utils/image.py` 是所有接口的前置依赖，Phase 1 优先写好
2. **异步**：所有数据库操作用 `async/await` + `aiosqlite`，FastAPI 本身就是异步的
3. **统一错误处理**：routes 里每个接口 try/except，返回 `{ "ok": false, "error": "..." }`
4. **AI 函数未就绪时**：先用 mock 数据调试——在 `services/deepseek.py` 里写个返回假数据的函数，你的 routes 可以独立测试
5. **静态文件**：`main.py` 里 `app.mount("/static"...)` 挂载目录，`mkdir static` 这步别忘了

---

## AI 服务 — 成员 2 职责

### 需要创建的文件

```
server/services/
├── deepseek.py         # ★ 核心：调用 DeepSeek Vision API
├── scoring.py          # ★ 评分计算 + 等级经验 + 勋章判定
└── composition.py      # 本地构图检测（水平线/主体位置/对称性）

server/prompts/
├── analyze.txt         # 修图+评分 prompt 模板
└── scene.txt           # 场景识别 prompt 模板
```

### 需要提供的函数（被传统后端调用）

```python
# services/deepseek.py

async def analyze_photo(image_base64: str) -> dict:
    """
    调 DeepSeek Vision API 做完整分析
    输入: base64 编码的照片
    返回: {
        scores: { composition, exposure, color, sharpness, creativity },
        summary: str,
        strengths: [str],
        weaknesses: [str],
        suggestions: [{category, tip}],
        tutorial_steps: [str],
        scene: { label, confidence }
    }
    """
    pass

async def detect_scene(image_base64: str) -> dict:
    """
    快速场景识别（低分辨率图）
    返回: { scene: "夜景", confidence: 0.87, params: { shutter, iso, wb } }
    """
    pass
```

```python
# services/scoring.py

def calculate_overall(scores: dict) -> int:
    """加权综合分 = 构图×0.3 + 曝光×0.25 + 色彩×0.2 + 清晰度×0.15 + 创意×0.1"""

def get_exp_for_analysis(overall_score: int) -> int:
    """一次分析获得多少经验"""

def check_level_up(current_exp: int, current_level: int) -> dict:
    """检查是否升级，返回 { level_up, new_level }"""

def check_badge_unlock(user_data: dict, new_analysis: dict) -> list:
    """检查是否解锁新勋章，返回 ['构图大师'] 或 []"""
```

```python
# services/composition.py

def detect_horizon_tilt(image_path: str) -> float:
    """检测水平线倾斜角度，返回度数"""

def detect_subject_position(image_path: str) -> str:
    """检测主体位置: left_third / center / right_third"""

def composition_score_boost(ai_scores: dict, image_path: str) -> dict:
    """补充本地检测结果，修正构图评分"""
```

### 注意事项

1. **Prompt 是最重要的代码**：产品同学负责迭代 prompt 文本，AI 同学负责调 API 参数（temperature、max_tokens）
2. **返回 JSON 不规整**：DeepSeek 有时会返回 ````json` 包裹的文本，需要正则清洗再 `json.loads()`
3. **用 config.py**：API Key 从 `config.py` 读，不要硬编码

---

## 快应用前端 — 成员 3 职责

### 需要创建的文件

```
src/
├── app.ux                  # 入口
├── manifest.json           # 路由 + features + permissions
├── store/index.js          # qa-vuex 状态管理
├── services/api.js         # 后端 API 调用封装
├── helper/
│   ├── image.js            # 前端图片压缩（轻量）
│   └── storage.js          # 本地缓存
│
├── Home/index.ux           # 首页
├── Camera/index.ux         # ① 相机 + 构图线 + 参数面板
├── Analysis/index.ux       # ②③ 雷达图 + 修图建议 + 评分
├── Growth/index.ux         # ③ 成长体系
└── Gallery/index.ux        # 历史记录
```

### 页面逻辑要求

**Camera 页**：
- 引入 UI 同学的 `CompositionLines` 和 `ParamPanel` 组件
- 接 Store 的 `camera.scene`、`camera.params`、`camera.gridMode`
- 首次进入调 `POST /api/scene/detect`（仅一次）
- 拍照后保存图片 → 调用 `POST /api/analyze` → 跳转 Analysis

**Analysis 页**：
- 接收上一页传参或 Store 里的 `analysis` 数据
- 使用 UI 同学的 `ScoreRadar` 组件展示雷达图
- 展示修图建议列表（可展开/折叠）
- 显示经验加成 + 勋章提示

**Growth 页**：
- 调 `GET /api/user/info` 获取用户数据
- 等级进度条 + 勋章墙 + 近 7 天评分趋势线
- 打卡按钮 → `POST /api/user/checkin`

**Gallery 页**：
- 调 `GET /api/gallery` 分页加载
- 使用 UI 同学的 `PhotoCard` 组件

### API 调用封装（services/api.js）

```javascript
const BASE = 'http://xxx:8000/api'

export function analyzePhoto(imageFile, sceneType) { ... }   // POST /api/analyze
export function detectScene(imageFile) { ... }               // POST /api/scene/detect
export function getUserInfo(uid) { ... }                     // GET /api/user/info
export function checkin(uid) { ... }                         // POST /api/user/checkin
export function getGallery(uid, page) { ... }                // GET /api/gallery
export function getGalleryDetail(id) { ... }                 // GET /api/gallery/:id
```

### 注意事项

1. **图片压缩在前端**：上传前先压缩至 1024px 最长边，大幅降低上传时间
2. **manifest.json 权限**：务必声明 `system.media`、`system.fetch`、`system.storage`、`system.sensor`
3. **所有 API 调用加 loading 态 + 错误提示**
4. **本地缓存**：分析结果存到 `system.storage`，离线也能看历史

---

## UI + 产品 — 成员 4 职责

### 需要创建的 UI 组件（src/Common/）

| 组件 | 用途 | 需定义的 props |
|------|------|----------------|
| `ScoreRadar.ux` | 五维雷达图 | `scores: {}` → Canvas 绘制 |
| `CompositionLines.ux` | 构图参考线叠加 | `mode: string`，`visible: boolean` |
| `ParamPanel.ux` | 参数推荐面板 | `params: {}`，`scene: string` |
| `PhotoCard.ux` | 照片卡片（列表用） | `item: { id, overall, scene, thumb_url, created_at }` |
| `LevelBadge.ux` | 等级/勋章展示 | `level: number`，`badges: []` |

### 页面样式规范

- 主色调统一
- 间距/字号/圆角规范
- 5 个页面的整体视觉风格

### 产品 + Prompt 职责

- 撰写 `prompts/analyze.txt` 和 `prompts/scene.txt`
- 与 AI 同学一起迭代测试 prompt（拍照 → 看 AI 返回 → 调整 prompt → 再测）
- 整理预设参数表（不同场景的默认参数，AI 不可用时的 fallback）
- 端到端测试（完整用户流程走通）
- 答辩材料（PPT + 演示流程 + Live Demo 脚本）

### 注意事项

1. **组件 = 模版 + 样式**：UI 同学先写好组件的 `<template>` 和 `<style>`，`<script>` 里只定义 props，具体逻辑留给前端同学
2. **Props 先行**：每个组件开始前，跟前端同学口头约定 props 名字和类型
3. **产品先行**：prompt 在 Phase 1 就开始写，AI 同学的代码调通后立刻测试

---

## 协作约定

### 接口合约（必须 Phase 1 结束前对齐）

```
传统后端 ←→ AI 服务       contract: Python 函数签名（services/deepseek.py）
传统后端 ←→ 前端           contract: HTTP API JSON 格式（上面 6 个接口的请求/响应）
前端     ←→ UI 组件        contract: 组件 props 定义
AI 服务  ←→ 产品           contract: prompt 模板文件 + 调参记录
```

### Phase 1 对齐清单

- [ ] 四人一起过一遍 ARCHITECTURE.md，确认理解一致
- [ ] 传统后端 + AI 服务：确认 `analyze_photo()` 和 `detect_scene()` 的输入输出类型
- [ ] 传统后端 + 前端：确认 6 个 API 的 JSON 格式（用 Postman/mock 数据验证）
- [ ] 前端 + UI：确认 5 个组件的 props 列表
- [ ] AI 服务 + 产品：确认 prompt 模板在哪、谁先写初稿

### 并行开发顺序

```
Phase 1 ────────────────────────────────────────────▶
  AI 服务：搭 services骨架 → 写 mock 返回假数据
  传统后端：database.py → utils/image.py → routes 骨架
  前端：5 页面占位 → store 结构 → services/api.js 封装
  UI：设计组件 → 写 CompositionLines/ParamPanel 初版
  产品：写 analyze.txt prompt 初稿

Phase 2 ────────────────────────────────────────────▶
  AI 服务：接入真实 DeepSeek API → 调 prompt
  传统后端：routes 真正调 AI 服务（替代 mock）
  前端：Camera 页接相机 + 接组件
  UI：ScoreRadar 组件
  产品：场景预设参数表 + prompt 迭代

Phase 3-4-5 以此类推...
```
