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
                    用户拍照/选图
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
       ┌────────┐  ┌────────┐  ┌────────┐
       │ ① 拍摄  │  │ ② 修图  │  │ ③ 评分  │
       │   指导  │  │   建议  │  │   评价  │
       └───┬────┘  └───┬────┘  └───┬────┘
           │            │            │
  场景：    相机取景     已拍照片     任意照片
  用户说： "这场景怎么拍" "这照片怎么修" "这照片打几分"
           │            │            │
  输入：    实时预览帧    拍完的照片    网上找的参考图
           │            │            │
  输出：    参数推荐      调色/修图     五维评分
           快门/ISO/WB   分步教程      优缺点
           场景标签      跳转修图App    等级成长
           │            │            │
  用户流： Camera 页    Analysis 页  Analysis 页
           拍照前        拍照后        任意时机
```

**三种模式由用户决定**：

| 模式 | 用户场景 | 输入来源 | 触发方式 |
|------|----------|----------|----------|
| ① 拍摄指导 | 正在拍摄地，用相机取景 | 实时预览帧 | Camera 页自动 + 手动刷新 |
| ② 修图建议 | 已拍完照片，想学调色修图 | 刚拍的照片 / 相册选图 | 选照片 → 点「修图建议」 |
| ③ 评分评价 | 想知道照片水平（包括网上找的参考图） | 任意照片 | 选照片 → 点「评分评价」 |

**同一张照片可以多次分析**：比如拍完后先做修图建议（②），修完后再做评分评价（③），两次调用不同的分析模式。

---

## 整体架构

```
┌─────────────────────────┐        HTTP/JSON       ┌──────────────────────────┐
│      快应用前端           │ ────────────────────▶ │     Python 后端           │
│    (Quick App)          │ ◀────────────────────  │   (FastAPI + uvicorn)    │
│                         │                       │                          │
│  ① Camera  拍照指导      │ ─ 上传预览帧 ────────▶ │  POST /api/analyze       │
│  ② Analysis 修图建议     │ ─ 上传照片 ────────▶ │    mode=shooting/edit    │
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

### SQLite 表结构（2 张表）

用户以**设备 ID** 标识，不需要登录系统。分析记录 FIFO 30 条，缩略图存 `static/` 目录。

```sql
-- 用户表
CREATE TABLE users (
    uid TEXT PRIMARY KEY,
    nickname TEXT DEFAULT '',
    level INTEGER DEFAULT 1,
    exp INTEGER DEFAULT 0,
    badges_json TEXT DEFAULT '[]',
    total_analyses INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 分析记录表（每人最多 30 条）
CREATE TABLE analyses (
    id TEXT PRIMARY KEY,
    uid TEXT NOT NULL,
    mode TEXT NOT NULL,
    result_json TEXT,
    thumb_url TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (uid) REFERENCES users(uid)
);
```

---
## 图片策略

| 角色 | 处理 |
|------|------|
| 前端 | 拍照/选图后上传，上传前压缩至 1024px |
| 后端 | 压缩图存 `static/` → 调 AI → 返回 JSON + thumb_url |
| Gallery | 直接 `<image src="服务器/static/xxx.jpg">` |

---

## 前端 — 快应用
## 前端 — 快应用

### 目录结构

```
project-root/
├── sign/debug/
├── src/
│   ├── app.ux                     # 应用入口
│   ├── manifest.json              # 路由 + 权限声明
│   │
│   ├── Camera/                        # ① 实时拍摄指导（首页入口）
│   │   └── index.ux                   # 相机 + 参数面板 + 构图线
│   │
│   ├── Upload/                        # 选图 + 选择分析模式
│   │   └── index.ux                   # 拍照/相册 → shooting/edit/score
│   │
│   ├── Result/                        # 分析结果展示
│   │   └── index.ux                   # 雷达图 + 修图建议 + 评分
│   │
│   ├── Gallery/                       # 历史记录
│   │   └── index.ux                   # 本地图片 + 后端 JSON
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
    "entry": "Camera",
    "pages": {
      "Camera":  { "component": "index" },
      "Upload":  { "component": "index" },
      "Result":  { "component": "index" },
      "Gallery": { "component": "index" }
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
| POST | `/api/analyze` | 照片分析（三种模式，Camera 页也用 shooting） | ①②③ |
| GET | `/api/user/info?uid=x` | 获取用户信息 | 成长体系 |
| GET | `/api/user/stats?uid=x` | 评分趋势数据 | 成长体系 |
| GET | `/api/gallery?uid=x` | 历史分析记录列表 | 记录回看 |
| GET | `/api/gallery/:id` | 单条分析详情 | 记录回看 |

### 核心接口 — POST /api/analyze（三种模式）

**同一个端点，通过 `mode` 参数区分**，三种模式用不同的 DeepSeek prompt，返回结构也不同：

```
请求: multipart/form-data
  image: <file>              # 照片（必填）
  mode: "shooting"|"edit"|"score"   # 三种模式（必填）

模式说明:
  shooting  → ① 拍摄指导   "看到这张参考图，我怎么拍出类似效果？"
  edit      → ② 修图建议   "这张照片有什么问题？怎么调色修图？"
  score     → ③ 评分评价   "这张照片打几分？构图曝光色彩怎么样？"
```

#### 模式 1: `mode=shooting` — 拍摄指导

```
用户场景: 在网上看到一张好看的照片，想知道怎么拍出类似效果
          （用户自己拍的也行——"这个场景我参数怎么调？"）

请求: { image, mode: "shooting" }
      后端调 AI 同学: from services.deepseek import shooting_advice(image_b64)

响应:
{
  "mode": "shooting",
  "scene": "夜景人像",
  "camera_params": {
    "shutter": "1/30",
    "iso": "800",
    "aperture": "f/2.8",
    "wb": "4000K",
    "focus": "人物面部单点对焦"
  },
  "composition_tips": [
    "人物置于右侧三分线，左侧留出城市灯光背景",
    "利用路灯作为前景，增加画面层次感"
  ],
  "lighting_advice": "利用街道灯光作为主光源，注意避免头顶路灯直射导致过曝",
  "extra_tips": "建议使用三脚架，夜间长曝光避免手抖"
}
```

#### 模式 2: `mode=edit` — 修图建议

```
用户场景: 已经拍完的照片，想知道怎么后期修图

请求: { image, mode: "edit" }
      后端调 AI 同学: from services.deepseek import editing_advice(image_b64)

响应:
{
  "mode": "edit",
  "issues": [
    {
      "category": "曝光",
      "severity": "high",
      "description": "背景天空过曝，丢失云层细节",
      "fix": "降低曝光 -0.5EV",
      "steps": ["打开亮度面板", "将曝光滑块左移至 -0.5", "用蒙版仅调整天空区域"]
    },
    {
      "category": "色彩",
      "severity": "medium",
      "description": "色温偏冷，肤色苍白",
      "fix": "白平衡调至 5500K",
      "steps": ["进入颜色面板", "色温滑块右移至 5500K", "自然饱和度 +10"]
    }
  ],
  "quick_fix": "推荐一键滤镜: 「暖日」或「胶片2」"
}
```

#### 模式 3: `mode=score` — 评分评价

```
用户场景: 拍完修完后想看评分，或者网上找的图想看看评价

请求: { image, mode: "score" }
      后端调 AI 同学: from services.deepseek import score_photo(image_b64)

响应:
{
  "mode": "score",
  "scores": {
    "composition": 85,
    "exposure": 72,
    "color": 80,
    "sharpness": 90,
    "creativity": 65
  },
  "overall": 78,
  "rating_label": "良好",
  "summary": "构图遵循三分法，人物主体清晰突出。背景过曝和色温偏冷是主要扣分项。",
  "strengths": [
    "人物主体位于三分线交点，构图均衡",
    "对焦准确，面部细节丰富"
  ],
  "weaknesses": [
    "背景天空过曝，丢失云层细节",
    "色温偏冷，肤色略显苍白"
  ],
  "exp_gained": 25,
  "badge_unlocked": null
}
```


## 全流程详解 — 单模型方案（MVP）

只用一个模型 `Volc-DeepSeek-V3.2`，三种模式共用同一个 API 地址，通过不同 prompt 切换。

### AI 模型配置

```python
# config.py
VIVO_API_KEY = "your_AppKey"
VIVO_BASE_URL = "https://api-ai.vivo.com.cn/v1"
MODEL_NAME = "Volc-DeepSeek-V3.2"
```

```python
# server/services/deepseek.py
from openai import OpenAI
from config import VIVO_API_KEY, VIVO_BASE_URL, MODEL_NAME

client = OpenAI(api_key=VIVO_API_KEY, base_url=VIVO_BASE_URL)

async def call_vision(prompt: str, image_base64: str, temperature=0.3, max_tokens=1024) -> str:
    """通用视觉调用"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }}
            ]
        }],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
```

---

### 模式一：shooting — 拍摄指导

```
用户流程:
  在网上看到好看的照片/参考图
  → 打开光影参谋 → 选图 → 点「拍摄指导」
  → 看到场景识别 + 参数建议 + 构图指导
```

**Prompt（server/prompts/shooting.txt）：**

```
你是一位专业摄影导师。看到这张照片，请告诉用户在类似场景下怎么拍出好照片。

请返回严格 JSON：
{
  "scene": "场景类型：人像/夜景/风景/美食/街拍/静物",
  "camera_params": {
    "shutter": "建议快门速度，如 1/125",
    "iso": "建议 ISO，如 400",
    "aperture": "建议光圈，如 f/2.8",
    "wb": "建议白平衡，如 5500K",
    "focus": "对焦建议，如 人物面部单点对焦"
  },
  "composition_tips": ["构图建议1", "构图建议2", "构图建议3"],
  "lighting_advice": "用光建议，30字以内",
  "extra_tips": "其他建议（设备、时机、角度等），30字以内"
}

规则：
1. 参数建议具体可用，适合手机拍照
2. 构图建议要有画面感，说清楚主体放哪里、怎么取景
3. 用光建议要结合画面中实际的光源方向
4. 其他建议可以提三脚架、闪光灯、最佳拍摄时间等
5. 只返回 JSON，不要任何其他文字。
```

**完整调用链：**

```
  快应用                    routes/analyze.py              services/deepseek.py            vivo API
  ──────                    ────────────────              ────────────────────            ────────
 用户选图,点「拍摄指导」
  → 图片压缩 1024px
  → POST /api/analyze
    { image, mode: "shooting" }
                              ① 收到请求
                              ② 图片 → compress → base64
                              ③ if mode == "shooting":
                                result = await shooting_advice(img_b64)
                                                            ④ call_vision(
                                                                 prompt=SHOOTING_PROMPT,
                                                                 image_b64=img_b64
                                                               )
                                                                                            ⑤ POST /v1/chat/completions
                                                                                               model: Volc-DeepSeek-V3.2
                                                                                               messages: [
                                                                                                 { role: "user",
                                                                                                   content: [
                                                                                                     { type: "text",
                                                                                                       text: shooting_prompt },
                                                                                                     { type: "image_url",
                                                                                                       url: "data:image/jpeg;base64,..." }
                                                                                                   ]}
                                                                                               ]
                                                                                               temperature: 0.3
                                                                                               max_tokens: 1024
                                                                                            ⑥ 返回 JSON
                                                            ⑦ 解析 JSON 字符串 → dict
                              ⑧ 存入 analyses 表
                              (mode="shooting")
                              ⑨ 返回给前端
 ⑩ 展示拍摄建议
```

**返回示例：**

```json
{
  "mode": "shooting",
  "id": "abc123",
  "scene": "夜景人像",
  "camera_params": {
    "shutter": "1/30",
    "iso": "800",
    "aperture": "f/2.8",
    "wb": "4000K",
    "focus": "人物面部单点对焦"
  },
  "composition_tips": [
    "人物置于画面右侧三分线，左侧留出城市灯光背景",
    "利用路边栏杆作为引导线，将视线引向人物"
  ],
  "lighting_advice": "利用街道暖色灯光作为主光源，避免头顶路灯直射导致面部过曝",
  "extra_tips": "建议使用三脚架，夜间慢速快门避免手抖"
}
```

---

### 模式二：edit — 修图建议

```
用户流程:
  已经拍完的照片，但是不满意效果
  → 打开光影参谋 → 选这张照片 → 点「修图建议」
  → 看到问题诊断 + 调色步骤 + 一键跳转修图App
```

**Prompt（server/prompts/edit.txt）：**

```
你是一位专业摄影后期导师。分析这张照片的后期处理问题，给出修图建议。

请返回严格 JSON：
{
  "issues": [
    {
      "category": "曝光/色彩/构图/清晰度/噪点/白平衡/对比度/饱和度",
      "severity": "high/medium/low",
      "description": "具体问题的简短描述，20字以内",
      "suggestion": "修图建议，20字以内",
      "tutorial_steps": ["步骤1", "步骤2", "步骤3"]
    }
  ],
  "quick_fix": "如果你在用修图App，一键推荐的滤镜或调整方向"
}

规则：
1. 只列出确实存在的问题，优点不列
2. 不要虚构缺陷，主观审美内容不评价
3. 修图步骤具体可操作，每一步都是手机修图App能做的
4. 语言通俗易懂，用户零修图基础
5. 只返回 JSON，不要任何其他文字。
```

**返回示例：**

```json
{
  "mode": "edit",
  "id": "abc456",
  "issues": [
    {
      "category": "曝光",
      "severity": "high",
      "description": "背景天空过曝，丢失云层细节",
      "suggestion": "降低曝光 -0.5EV",
      "tutorial_steps": ["打开修图App亮度面板", "曝光滑块左移至 -0.5", "使用蒙版仅调整天空区域"]
    },
    {
      "category": "色温",
      "severity": "medium",
      "description": "色温偏冷，肤色显苍白",
      "suggestion": "白平衡调至 5500K",
      "tutorial_steps": ["进入颜色/白平衡面板", "色温滑块右移至 5500K", "自然饱和度 +10"]
    }
  ],
  "quick_fix": "推荐滤镜「暖日」或「胶片2」，可快速改善色温和层次"
}
```

---

### 模式三：score — 评分评价

```
用户流程:
  拍完/修完后想看照片到底好不好
  或者网上找的图想看看专业评价
  → 选照片 → 点「评分评价」
  → 看到五维雷达图 + 优缺点 + 经验值变化
```

**Prompt（server/prompts/score.txt）：**

```
你是一位专业摄影评委。对这张照片进行评分和评价。

评分标准：
- 构图(30%)：主体位置、画面平衡、三分法、引导线、对称性
- 曝光(25%)：明暗均衡、高光保留、阴影细节
- 色彩(20%)：白平衡、色彩和谐、饱和度控制
- 清晰度(15%)：对焦准确度、边缘锐度、噪点控制
- 创意(10%)：视角独特性、表现力、故事感、情感传达

请返回严格 JSON：
{
  "scores": {
    "composition": 0-100,
    "exposure": 0-100,
    "color": 0-100,
    "sharpness": 0-100,
    "creativity": 0-100
  },
  "overall": 0-100,
  "rating_label": "优秀/良好/一般/需改进",
  "summary": "总体评价，40字以内",
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["缺点1", "缺点2"]
}

规则：
1. 评分客观严格，不要虚高也不要恶意压低
2. 评语具体，指出好在哪、差在哪
3. 优缺点各 2-3 条
4. 只返回 JSON，不要任何其他文字。
```

**返回示例：**

```json
{
  "mode": "score",
  "id": "abc789",
  "scores": {
    "composition": 85,
    "exposure": 72,
    "color": 80,
    "sharpness": 90,
    "creativity": 65
  },
  "overall": 78,
  "rating_label": "一般",
  "summary": "构图遵循三分法，人物主体清晰，背景过曝和色温偏冷是主要扣分项",
  "strengths": ["人物主体位于三分线交点，构图均衡", "对焦准确，面部细节丰富"],
  "weaknesses": ["背景天空过曝，丢失云层细节", "色温偏冷，肤色略显苍白"],
  "exp_gained": 25,
  "badge_unlocked": null
}
```

---

### 三种模式对比

| | shooting | edit | score |
|------|---------|------|-------|
| 用户场景 | "这图怎么拍" | "这照片怎么修" | "这照片打几分" |
| vivo API 调用 | 1 次 | 1 次 | 1 次 |
| 模型 | DeepSeek | DeepSeek | DeepSeek |
| max_tokens | 1024 | 1024 | 1024 |
| 存数据库 | ✅ | ✅ | ✅ |
| 更新经验 | ❌ | ❌ | ✅ 仅评分更新 |
| 检查勋章 | ❌ | ❌ | ✅ |

---

### routes/analyze.py 核心实现（重构后 — 薄层）

```python
# routes/analyze.py — 只负责接收请求、分发到业务层
from fastapi import APIRouter, UploadFile, Form
from services.photo_analysis import shooting, edit, score

router = APIRouter(prefix="/api", tags=["analyze"])
HANDLERS = {"shooting": shooting, "edit": edit, "score": score}

@router.post("/analyze")
async def analyze(image: UploadFile, mode: str = Form(...), uid: str = Form(...)):
    if mode not in HANDLERS:
        return {"ok": False, "error": f"未知模式: {mode}"}
    return {"ok": True, "data": await HANDLERS[mode](uid, image)}
```

### services/photo_analysis.py 核心实现（业务编排层）

```python
# services/photo_analysis.py — 编排完整分析流程
# 压缩图片 → 调 AI → 计算经验 → 更新用户 → 存库 → 返回

async def shooting(uid, image):
    img_b64 = await compress_to_base64(image)
    result = await shooting_advice(img_b64)
    result["id"] = await save_analysis(uid, "shooting", result)
    return result

async def edit(uid, image):
    img_b64 = await compress_to_base64(image)
    result = await editing_advice(img_b64)
    result["id"] = await save_analysis(uid, "edit", result)
    return result

async def score(uid, image):
    img_b64 = await compress_to_base64(image)
    result = await score_photo(img_b64)
    exp_gained = EXP_PER_ANALYSIS
    if result["overall"] >= 90: exp_gained += EXP_PERFECT_SCORE
    elif result["overall"] >= 80: exp_gained += EXP_HIGH_SCORE
    result["exp_gained"] = exp_gained
    result["level_up"] = await update_user_exp(uid, exp_gained)
    result["badge_unlocked"] = await check_badge_unlock(uid, result)
    result["id"] = await save_analysis(uid, "score", result)
    return result
    
    result["id"] = await save_analysis(uid, mode, result)
    result["mode"] = mode
    return {"ok": True, "data": result}
```

---

### 复赛储备：RAG 增强方案

初赛用上面单模型方案跑通后，复赛可加 RAG 知识库增强建议质量。

**新增 vivo 模型**：`bge-base-zh-v1.5`（向量化） + `bge-reranker-large`（精排）

**流程**：DeepSeek 先识别场景 → Embedding API 向量化 → 知识库相似度检索 → Rerank 精排 Top 3 → 检索结果拼入 prompt → DeepSeek 生成增强建议

**知识库格式**（server/knowledge/photography.json）：

```json
[
  {
    "id": "night_001",
    "topic": "夜景拍摄",
    "tags": ["夜景", "低光", "慢快门"],
    "text": "夜景拍摄要点：1. 三脚架防手抖；2. ISO 800-1600、快门 1/15-1/30s；3. 白平衡 4000K；4. 手动对焦对准光源；5. 关闭闪光灯用环境光。",
    "embedding": null
  }
]
```

**预计增加延迟** ~1 秒（Embedding + Rerank）。


### 后端目录结构

```
server/
├── main.py                    # FastAPI 入口
├── config.example.py          # 配置模板
├── requirements.txt           # 依赖
│
├── routes/                    # HTTP 层 — 只收请求、调 service、返回
│   ├── analyze.py             #   15行：收 mode → 调 photo_analysis → 返回
│   ├── scene.py               #   10行：收 preview → 调 AI → 返回
│   ├── user.py                #   15行：收 uid → 调 model → 返回
│   └── gallery.py             #   10行：收 uid → 调 model → 返回
│
├── services/                  # 业务编排 + AI 调用
│   ├── photo_analysis.py      # ★ 照片分析的完整编排（压缩→AI→存库→经验→返回）
│   ├── deepseek.py            # DeepSeek Vision API 封装 + 4 个 AI 函数
│   ├── scoring.py             # 评分规则 + 等级判定 + 勋章规则
│   └── composition.py         # 本地构图检测
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
├── static/                  # 压缩图存储（Gallery 直接读）
└── prompts/                 # 3 个 Prompt 模板
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
- 场景识别 prompt 调优（Camera 页调用 shooting 模式）

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

### 项目文件归属

```
图例:
  🔴 传统后端（你）      🔵 AI 服务（成员 2）
  🟢 快应用前端（成员 3）  🟡 UI+产品（成员 4）
  ⚪ 共享契约（双方对齐即可）


photography-partner/
│
├── 📄 README.md              🟡 UI+产品
├── 📄 ARCHITECTURE.md        ⚪ 共享
├── 📄 CLAUDE.md              ⚪ 共享
├── 📄 .gitignore             🔴 后端
│
├── 📁 sign/debug/            🟢 前端
│
├── 📁 src/                   ─── 快应用前端 ───
│   ├── manifest.json          🟢 前端
│   ├── app.ux                 🟢 前端
│   │
│   ├── 📁 Camera/
│   │   └── index.ux           🟢 前端（逻辑） + 🟡 UI（样式）
│   │
│   ├── 📁 Upload/
│   │   └── index.ux           🟢 前端（逻辑） + 🟡 UI（样式）
│   │
│   ├── 📁 Result/
│   │   └── index.ux           🟢 前端（逻辑） + 🟡 UI（样式）
│   │
│   ├── 📁 Gallery/
│   │   └── index.ux           🟢 前端（逻辑） + 🟡 UI（样式）
│   │
│   ├── 📁 Common/             ─── 🟡 UI 同学的主战场 ───
│   │   ├── ScoreRadar.ux       🟡 UI（模板+样式） + 🟢 前端（数据绑定）
│   │   ├── CompositionLines.ux 🟡 UI（模板+样式） + 🟢 前端（数据绑定）
│   │   ├── ParamPanel.ux       🟡 UI（模板+样式） + 🟢 前端（数据绑定）
│   │   ├── PhotoCard.ux        🟡 UI（模板+样式） + 🟢 前端（数据绑定）
│   │   └── LevelBadge.ux       🟡 UI（模板+样式） + 🟢 前端（数据绑定）
│   │
│   ├── 📁 store/
│   │   └── index.js            🟢 前端
│   │
│   ├── 📁 services/
│   │   └── api.js              🟢 前端（封装请求）← ⚪ 与 🔴 后端对齐 JSON 格式
│   │
│   └── 📁 helper/
│       ├── image.js            🟢 前端
│       └── storage.js          🟢 前端
│
├── 📁 server/                 ─── Python 后端 ───
│   ├── main.py                 🔴 后端
│   ├── config.example.py       🔴 后端
│   ├── requirements.txt        🔴 后端
│   │
│   ├── 📁 routes/              ─── 🔴 传统后端 主战场 ───
│   │   ├── analyze.py           🔴 后端 ← 调 🔵 AI 服务的函数
│   │   ├── user.py              🔴 后端（纯 CRUD，不调 AI）
│   │   └── gallery.py           🔴 后端（纯 CRUD，不调 AI）
│   │
│   ├── 📁 services/            ─── 混合领域 ───
│   │   ├── photo_analysis.py    🔴 后端（编排：压缩→调AI→存库→经验→返回）
│   │   ├── deepseek.py          🔵 AI（3 个 AI 函数：shooting/edit/score）
│   │   ├── scoring.py           🔵 AI（评分规则 + 等级判定 + 勋章规则）
│   │   └── composition.py       🔵 AI（本地构图检测算法）
│   │
│   ├── 📁 prompts/             ─── 🔵 AI + 🟡 产品 协作 ───
│   │   ├── shooting.txt         🟡 产品（写 Prompt） + 🔵 AI（调参数）
│   │   ├── edit.txt             🟡 产品（写 Prompt） + 🔵 AI（调参数）
│   │   ├── score.txt            🟡 产品（写 Prompt） + 🔵 AI（调参数）
│   │   └── scene.txt            🟡 产品（写 Prompt） + 🔵 AI（调参数）
│   │
│   ├── 📁 models/
│   │   └── database.py          🔴 后端
│   │
│   ├── 📁 utils/
│   │   ├── image.py             🔴 后端
│   │   └── response.py          🔴 后端
│   │
│   ├── 📁 knowledge/           ─── 🟡 产品（摄影知识库，复赛用）───
│   │   └── photography.json     🟡 产品
│   │
│   ├── 📁 data/                 🔴 后端（SQLite 自动生成，不提交）
│   └── 📁 static/               🔴 后端（图片缩略图）
```

### 各角色不碰的文件（硬边界）

| 角色 | 绝不修改 | 原因 |
|------|---------|------|
| 🔴 后端 | `services/deepseek.py` `services/scoring.py` `services/composition.py` `prompts/` `src/` | AI 纯函数归 AI 同学；前端归前端。可以改 `services/photo_analysis.py` |
| 🔵 AI | `routes/` `models/` `utils/` `services/photo_analysis.py` `src/` | 只提供 deepseek/scoring/composition 里的纯函数，不管 HTTP/数据库/编排 |
| 🟢 前端 | `server/` 全部 | 只调 API，不管后端实现 |
| 🟡 UI | `server/` `src/store/` `src/services/` | 只写组件样式和 prompt 文本 |

### 协作接口（Contract）

```
🟢 前端 ←→ 🔴 后端      HTTP JSON（6 个 API 的请求/响应格式）
                           对齐文件: src/services/api.js ↔ server/routes/*.py

🔴 后端 ←→ 🔵 AI        Python 函数签名（services/photo_analysis.py 调 services/deepseek.py 的 4 个函数）
                           对齐文件: services/deepseek.py 的 shooting_advice / editing_advice / score_photo / detect_scene

🟢 前端 ←→ 🟡 UI       组件 props
                           对齐文件: src/Common/*.ux 里的 props 定义

🔵 AI  ←→ 🟡 产品      Prompt 模板
                           对齐文件: server/prompts/*.txt
```

### 四人分工

| 角色 | 谁 | 文件范围 | 一句话 |
|------|-----|----------|--------|
| 🔴 **传统后端** | 你 | `server/routes/` `server/services/photo_analysis.py` `server/models/` `server/utils/` `server/main.py` `server/config.py` | HTTP → 编排 → 调 AI 函数 → 数据库 → JSON |
| 🔵 **AI 服务** | 成员 2 | `server/services/deepseek.py` `server/services/scoring.py` `server/services/composition.py` | 4 个纯函数给后端编排层调用，不碰 HTTP/数据库 |
| 🟢 **快应用前端** | 成员 3 | `src/Camera/` `src/Upload/` `src/Result/` `src/Gallery/` `src/store/` `src/services/api.js` `src/helper/` `src/app.ux` `src/manifest.json` | 页面逻辑、状态管理、API 调用、相机接入 |
| 🟡 **UI + 产品** | 成员 4 | `src/Common/ScoreRadar.ux` `src/Common/CompositionLines.ux` `src/Common/ParamPanel.ux` `src/Common/PhotoCard.ux` `src/Common/LevelBadge.ux` `server/prompts/shooting.txt` `server/prompts/edit.txt` `server/prompts/score.txt` `server/prompts/scene.txt` `server/knowledge/` | 组件 UI + Prompt 撰写 + 测试 + 答辩 |

**页面 ux 文件的协作方式**（🟢 + 🟡）：
- 🟡 UI 先写 `<template>` 和 `<style>`
- 🟢 前端再写 `<script>` 逻辑和数据绑定
- 不要同时改同一个 ux 文件

---

## 传统后端 — 你的职责

### 你需要创建的文件

```
server/
├── main.py                 # FastAPI 入口，注册路由，挂载静态文件
├── config.py               # 数据库路径、DeepSeek API Key、端口等配置
│
├── routes/                 # ★ 路由层：接收请求 → 调 AI 服务 → 操作数据库 → 返回响应
│   ├── analyze.py          # POST /api/analyze（三种模式，Camera 也用 shooting）
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

### 你需要实现的 5 个接口

#### 1. `POST /api/analyze` — 核心（三种模式）

```
输入: multipart/form-data { image: File, mode: "shooting" | "edit" | "score" }

你的处理流程:
  ① 从 UploadFile 读取图片 bytes
  ② 调 utils/image.py → compress_to_1024() → to_base64()
  ③ 根据 mode 调 AI 同学的不同函数:
     if mode == "shooting":
         result = await shooting_advice(image_base64)
     elif mode == "edit":
         result = await editing_advice(image_base64)
     elif mode == "score":
         result = await score_photo(image_base64)
  ④ 存数据库: INSERT INTO analyses (mode 字段记录是哪类分析)
  ⑤ 如果 mode == "score": 更新用户经验、检查升级/勋章
     （shooting 和 edit 不涉及成长体系）
  ⑥ 返回结果给前端

响应: 因 mode 不同而不同（见上文三种模式的合约）
```

#### 2. `GET /api/user/info?uid=xxx`

```
处理流程:
  ① 查 users 表
  ② 有记录 → 返回
  ③ 无记录 → INSERT 新用户 (level=1, exp=0) → 返回

响应: { uid, level, exp, badges, streak, total_analyses, last_checkin }
```

#### 4. `GET /api/gallery?uid=xxx&page=1&size=20`

```
处理流程:
  ① 查 analyses 表 WHERE uid=? ORDER BY created_at DESC
  ② 分页返回

响应: { items: [{ id, overall, scene, thumb_url, created_at }], total, page }
```

#### 5. `GET /api/gallery/:id`

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
- 首次进入调 `POST /api/analyze` mode=shooting（仅一次）
- 拍照后保存图片 → 调 mode=score/edit → 跳转 Analysis

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

---

## 分工解耦：谁通过什么接口跟谁联系

```
┌─────────────────────────────────────────────────────────────────────┐
│                         四人协作关系图                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  🟡 产品                          🟡 产品                           │
│   prompt 文本 ──────────────────▶ prompts/*.txt                     │
│                                    │                                │
│                                    ▼                                │
│                              🔵 AI 服务                             │
│   prompts/*.txt ──────────▶ deepseek.py                             │
│                               shooting_advice(img_b64) → dict       │
│                               editing_advice(img_b64) → dict        │
│                               score_photo(img_b64) → dict           │
│                                    │                                │
│                                    │ Python 函数调用                  │
│                                    ▼                                │
│                              🔴 传统后端                             │
│  photo_analysis.py ───────── 调 AI 函数 + 调 database               │
│       │                          │                                  │
│       │ 编排                      │ 读写                             │
│       ▼                          ▼                                  │
│  routes/analyze.py          models/database.py                      │
│  routes/user.py              get_or_create_user()                   │
│  routes/gallery.py           save_analysis()                        │
│       │                      get_analyses()                         │
│       │ HTTP JSON            update_user_exp()                      │
│       ▼                      check_badge_unlock()                   │
│  ┌─────────────┐                                                     │
│  │  HTTP API   │  ←── 🟢 前端 通过 api.js 调用                       │
│  │  5 个端点    │      upload('/analyze', file, mode)                │
│  │             │      request('GET', '/user/info?uid=...')          │
│  └─────────────┘      request('GET', '/gallery?uid=...')            │
│         │                                                            │
│         │ JSON                                                       │
│         ▼                                                            │
│  🟢 前端 页面逻辑            🟡 UI 组件                              │
│   Camera/Upload/            Common/                                  │
│   Result/Gallery            ScoreRadar / CompositionLines            │
│       │                      ParamPanel / PhotoCard / LevelBadge     │
│       │ props                       │                                │
│       └──────────────────────────────┘                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 四条解耦边界

| 边界 | 谁↔谁 | 合约形式 | 具体文件 |
|------|-------|---------|---------|
| **① 产品 → AI** | 🟡 ↔ 🔵 | Prompt 文本文件 | `prompts/shooting.txt` `prompts/edit.txt` `prompts/score.txt` |
| **② AI → 后端** | 🔵 ↔ 🔴 | Python 函数签名 | `deepseek.py` 的 3 个 `async def` 函数 |
| **③ 后端 → 前端** | 🔴 ↔ 🟢 | HTTP JSON | 5 个 API 端点（见接口清单） |
| **④ UI → 前端** | 🟡 ↔ 🟢 | 组件 props | `Common/` 下 5 个 `.ux` 组件的 props 定义 |

### 各人只需要知道的接口

**🔴 传统后端（你）只需要知道：**

```python
# 从 AI 服务拿到的 3 个函数（不用关心内部怎么调 API、prompt 怎么写）
from services.deepseek import shooting_advice, editing_advice, score_photo

# 使用方式
result = await shooting_advice(image_base64)  # → dict
result = await editing_advice(image_base64)   # → dict
result = await score_photo(image_base64)       # → dict

# 你需要提供给前端的 5 个 HTTP 端点
POST /api/analyze     # { image, mode, uid } → { result, thumb_url }
GET  /api/user/info   # ?uid=xxx → { level, exp, badges }
GET  /api/user/stats  # ?uid=xxx → { recent_scores }
GET  /api/gallery     # ?uid=xxx&page=1 → { items, total }
GET  /api/gallery/:id # → 单条详情
```

**🔵 AI 服务只需要知道：**

```python
# 需要实现的 3 个函数（不用关心 HTTP、数据库）
async def shooting_advice(image_base64: str) -> dict: ...
async def editing_advice(image_base64: str) -> dict: ...
async def score_photo(image_base64: str) -> dict: ...
```

**🟢 前端只需要知道：**

```javascript
// 5 个 API（不用关心后端怎么实现）
POST /api/analyze     // 上传图片 + mode → 拿结果
GET  /api/user/info   // 拿用户等级经验
GET  /api/user/stats  // 拿评分趋势
GET  /api/gallery     // 拿历史列表（含 thumb_url）
GET  /api/gallery/:id // 拿单条详情

// 5 个组件的 props（不用关心组件内部样式）
<score-radar scores="{{scores}}">
<composition-lines mode="{{gridMode}}" visible="{{true}}">
<param-panel params="{{params}}" scene="{{scene}}">
<photo-card item="{{item}}">
<level-badge level="{{level}}" badges="{{badges}}">
```

**🟡 UI+产品 只需要知道：**

```html
<!-- 5 个组件，定义好 props -->
<!-- UI 写 <template> + <style>，前端写 <script> -->

<!-- ScoreRadar.ux -->     props: { scores: {} }
<!-- CompositionLines.ux --> props: { mode: '', visible: false }
<!-- ParamPanel.ux -->      props: { params: {}, scene: '' }
<!-- PhotoCard.ux -->       props: { item: {} }
<!-- LevelBadge.ux -->      props: { level: 0, badges: [] }
```

### 总结：一个人改代码，其他人不受影响

| 改动 | 只影响 |
|------|--------|
| 改 Prompt 文案 | 只改 `prompts/*.txt`，🔵 AI 同学不需要改代码 |
| 换 AI 模型 | 只改 `services/deepseek.py`，🔴 后端和 🟢 前端无感 |
| 改数据库字段 | 只改 `models/database.py` 和 `routes/` |
| 改前端页面布局 | 只改 `src/*/index.ux`，后端无感 |
| 改组件样式 | 只改 `src/Common/*.ux` 的 `<style>`，前端逻辑不受影响 |
