# API 接口文档

> 后端 ↔ 前端 | 数据契约 | 字段名即法律

---

## 统一响应格式

```json
// 成功
{ "ok": true,  "data": { ... } }

// 失败
{ "ok": false, "error": "错误原因" }
```

HTTP 状态码：`200` 正常 | `400` 参数错误 | `500` 服务器错误

---

## 接口清单

| 方法 | 端点 | 用途 |
|------|------|------|
| POST | `/api/analyze` | 照片分析（三种模式） |
| GET | `/api/user/info?uid=xxx` | 用户信息 |
| GET | `/api/gallery?uid=xxx&page=1&size=20` | 历史列表 |
| GET | `/api/gallery/{id}` | 单条详情 |

---

## POST /api/analyze

### 请求

```
Content-Type: multipart/form-data

image:  <File>      # JPEG，前端压缩至 1024px
mode:   "shooting" | "edit" | "score"
uid:    "device_xxx"  # 设备 ID
```

### mode=shooting — 拍摄指导

**AI 职责**（`services/deepseek.py → shooting_advice`）：返回以下 JSON。

```json
{
  "ok": true,
  "data": {
    "id": "uuid",
    "mode": "shooting",
    "thumb_url": "/static/abc123.jpg",
    "scene": "夜景人像",
    "camera_params": {
      "shutter": "1/30",
      "iso": "800",
      "aperture": "f/2.8",
      "wb": "4000K",
      "focus": "人物面部单点对焦"
    },
    "composition_tips": [
      "人物置于画面右侧三分线",
      "利用路边栏杆作引导线"
    ],
    "lighting_advice": "利用街道暖色灯光作主光源",
    "extra_tips": "建议使用三脚架"
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| scene | string | 场景类型：人像/夜景/风景/美食/街拍/静物 |
| camera_params.shutter | string | 建议快门速度 |
| camera_params.iso | string | 建议 ISO |
| camera_params.aperture | string | 建议光圈 |
| camera_params.wb | string | 建议白平衡 |
| camera_params.focus | string | 对焦建议 |
| composition_tips | string[] | 构图建议，2-3 条 |
| lighting_advice | string | 用光建议，30 字以内 |
| extra_tips | string | 其他建议 |

### mode=edit — 修图建议

**AI 职责**（`services/deepseek.py → editing_advice`）：返回纯文本，不包 JSON。

```json
{
  "ok": true,
  "data": {
    "id": "uuid",
    "mode": "edit",
    "thumb_url": "/static/def456.jpg",
    "advice": "这张照片可以先调一下色温，往暖色偏一点约 5500K，让肤色看起来更自然。然后亮度面板曝光 +0.3..."
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| advice | string | AI 修图建议纯文本，前端原样展示 |

### mode=score — 评分评价

**AI 职责**（`services/deepseek.py → score_photo`）：返回 `{ score, comment }` JSON。

```json
{
  "ok": true,
  "data": {
    "id": "uuid",
    "mode": "score",
    "thumb_url": "/static/ghi789.jpg",
    "score": 78,
    "comment": "这张照片整体不错！构图把人物放在三分线位置很舒服。可以改进的是背景稍微过曝了，下次试试降低曝光补偿。",
    "exp_gained": 25,
    "level_up": null,
    "badge_unlocked": null
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| score | int | 评分 0-100 |
| comment | string | AI 评价纯文本，前端原样展示 |
| exp_gained | int | 本次获得经验 |
| level_up | object\|null | `{ level_up, old_level, new_level }` 或 null |
| badge_unlocked | string[]\|null | 新勋章名列表 或 null |

---

## GET /api/user/info

### 请求

```
GET /api/user/info?uid=device_xxx
```

### 响应

```json
{
  "ok": true,
  "data": {
    "uid": "device_xxx",
    "nickname": "",
    "level": 3,
    "exp": 420,
    "badges": ["高分达人", "首战告捷"],
    "total_analyses": 23
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| uid | string | 设备 ID |
| level | int | 等级 1-6 |
| exp | int | 总经验值 |
| badges | string[] | 已获勋章列表 |
| total_analyses | int | 累计分析次数 |

---

## GET /api/gallery

### 请求

```
GET /api/gallery?uid=device_xxx&page=1&size=20
```

### 响应

```json
{
  "ok": true,
  "data": {
    "items": [
      {
        "id": "uuid",
        "mode": "score",
        "thumb_url": "/static/ghi789.jpg",
        "result_json": { "score": 78, "comment": "..." },
        "created_at": "2026-05-13 12:00:00"
      }
    ],
    "total": 30,
    "page": 1
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| items[].id | string | 记录 ID |
| items[].mode | string | shooting / edit / score |
| items[].thumb_url | string | 缩略图地址 |
| items[].result_json | object | 完整的分析结果（结构因 mode 而异） |
| items[].created_at | string | 时间戳 |
| total | int | 总记录数 |
| page | int | 当前页码 |

### 前端渲染建议

根据 `mode` 字段渲染不同卡片：

```
mode=shooting  →  显示 scene + camera_params 摘要
mode=edit      →  显示 advice 前 50 字
mode=score     →  显示 "⭐ score 分" + comment 前 50 字
```

---

## GET /api/gallery/{id}

### 请求

```
GET /api/gallery/abc123-def456-...
```

### 响应

```json
{
  "ok": true,
  "data": {
    "id": "abc123",
    "uid": "device_xxx",
    "mode": "shooting",
    "thumb_url": "/static/abc123.jpg",
    "result_json": { "scene": "夜景人像", "camera_params": {...} },
    "created_at": "2026-05-13 12:00:00"
  }
}
```

与 `/api/gallery` 的 item 结构相同，包含完整 `result_json`。

---

## 前后端协作速查

| 角色 | 输入 | 输出 | 依据 |
|------|------|------|------|
| 🔵 AI（deepseek.py） | base64 图片 | shooting→JSON / edit→str / score→JSON | `prompts/` 下的 txt，此文档的字段表 |
| 🔴 后端（routes） | UploadFile + mode | `{ ok, data }` | `schemas/response.py` Pydantic 模型 |
| 🟢 前端（api.js） | image + mode | 渲染 data 字段 | 此文档的每个接口示例 |
