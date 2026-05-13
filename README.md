# 光影参谋

一站式 AI 摄影构图成长伴侣 | 快应用 | vivo AIGC 创新赛

## 技术栈

- **前端**: 快应用 (Quick App / hap)
- **后端**: Python + FastAPI + SQLite
- **AI**:  Volc-DeepSeek-V3.2 (vivo API) + bge-base-zh-v1.5 (RAG 复赛)

## 项目结构

```
├── src/                    # 快应用前端
│   ├── Home/               # 首页入口
│   ├── Camera/             # ① 实时拍摄指导
│   ├── Analysis/           # ②③ 修图建议 + 评分评价
│   ├── Growth/             # ③ 成长体系
│   ├── Gallery/            # 历史画廊
│   ├── Common/             # 共享组件
│   ├── store/              # qa-vuex 状态管理
│   └── services/           # API 调用封装
├── server/                 # Python 后端
│   ├── routes/             # 路由层（传统后端）
│   ├── services/           # AI 服务层
│   ├── models/             # 数据库
│   ├── prompts/            # Prompt 模板
│   └── utils/              # 工具函数
└── ARCHITECTURE.md         # 完整架构书
```

## 快速开始

```bash
# 后端
cd server
pip install -r requirements.txt
cp config.example.py config.py  # 编辑 config.py 填入 AppKey
python main.py                   # → http://localhost:8000

# 前端（需先安装 hap-toolkit）
npm install -g hap-toolkit
npm install
npm run dev
```

## 团队分工

参见 [ARCHITECTURE.md](./ARCHITECTURE.md) — 团队分工章节。
