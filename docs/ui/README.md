# 光影参谋 UI 设计规范

> 纯 UI 交付物 | 前端同学直接复制粘贴

---

## 色彩系统

| 用途 | 色值 | 说明 |
|------|------|------|
| 页面背景 | `#0f0f23` | 深邃夜空黑 |
| 卡片/Header 背景 | `#1a1a2e` | 次级深色 |
| 分隔线/轨道底色 | `#2a2a3e` | 灰蓝 |
| 主色（金色） | `#ffd700` | 标题、重点、按钮 |
| 文字主色 | `#ffffff` | 标题 |
| 文字次要 | `#cccccc` | 正文 |
| 文字辅助 | `#888888` | 说明文字 |
| 文字弱化 | `#666666` | 占位符 |
| 文字极弱 | `#555555` | 日期等 |
| 成功绿 | `#4caf50` | 高分 |
| 警告橙 | `#ff9800` | 中分 |
| 错误红 | `#f44336` | 低分 |
| 拍摄模式 | `#4d96ff` | 蓝 |
| 修图模式 | `#c084fc` | 紫 |
| 评分模式 | `#ffd700` | 金 |
| 经验背景 | `#2a2a1e` | 暗金 |
| 升级背景 | `#1e2a1e` | 暗绿 |

---

## 等级颜色

| Lv | 称号 | 颜色 |
|----|------|------|
| 1 | 摄影新手 | `#9e9e9e` 灰 |
| 2 | 摄影学徒 | `#81c784` 浅绿 |
| 3 | 摄影达人 | `#4fc3f7` 浅蓝 |
| 4 | 摄影专家 | `#ba68c8` 紫 |
| 5 | 摄影大师 | `#ffd700` 金 |
| 6 | 光影艺术家 | `#ff6d00` 橙 |

---

## 五维评分颜色

| 维度 | 颜色 | 权重 |
|------|------|------|
| 构图 | `#ff6b6b` | 30% |
| 曝光 | `#ffd93d` | 25% |
| 色彩 | `#6bcb77` | 20% |
| 清晰度 | `#4d96ff` | 15% |
| 创意 | `#c084fc` | 10% |

---

## 字号体系

| 用途 | 字号 |
|------|------|
| 大标题（页面名） | 36px |
| 页面标题 | 18px |
| 区块标题 | 16px |
| 正文 | 15px |
| 辅助说明 | 13px |
| 次要文字 | 12px |
| 日期/提示 | 11px |
| 大分数 | 72px |
| 等级数字 | 48px |

---

## 间距体系

| 用途 | 值 |
|------|-----|
| 页面内边距 | 20px |
| 卡片内边距 | 16px |
| Header 高度 | 48px |
| 卡片圆角 | 12px (卡片) / 16px (大容器) |
| 按钮圆角 | 8px |
| 标签圆角 | 20px |
| 进度条高度 | 6px ~ 8px |

---

## 组件清单

| 组件文件 | 所属页面 | 说明 |
|----------|----------|------|
| `TopBar.ux` | 通用 | 顶部导航栏 |
| `BottomNav.ux` | 通用 | 底部导航标签栏 |
| `CameraBox.ux` | Camera | 预览区 + 三分法/黄金/十字构图线 |
| `ShootButton.ux` | Camera | 圆形拍照按钮 |
| `GridControl.ux` | Camera | 构图线切换按钮组 |
| `ParamPanel.ux` | Camera/Result | 推荐参数面板（5项） |
| `SceneTag.ux` | Camera/Result | 场景标签 |
| `ScoreCircle.ux` | Result | 评分大字 + 评价标签 |
| `ScoreRadar.ux` | Result | 五维评分条形图 |
| `AdviceCard.ux` | Result | 修图建议文本卡片 |
| `IssueCard.ux` | Result | 问题诊断卡片 |
| `BulletList.ux` | Result | 要点列表（构图建议等） |
| `ExpGainCard.ux` | Result | 经验获得提示 |
| `LevelUpCard.ux` | Result | 升级提示 |
| `BadgeUnlockCard.ux` | Result | 勋章解锁提示 |
| `PhotoCard.ux` | Gallery | 历史记录卡片 |
| `LevelBadge.ux` | Growth | 等级勋章（含进度条） |
| `BadgeTag.ux` | Growth | 勋章标签 |
| `StatsPanel.ux` | Growth | 统计面板（3列数据） |
| `ModeSelector.ux` | Upload | 三种模式选择器 |
| `ImagePicker.ux` | Upload | 选图/拍照入口 |
| `LoadingOverlay.ux` | 通用 | 加载遮罩 |

---

## 使用方式

前端同学在 `src/Common/` 下创建同名 `.ux` 文件，
每个文件在 `<template>` 和 `<style>` 段基础上，
**自行添加 `<script>` 段** 处理 props、事件和数据绑定。

示例：

```html
<!-- 复制 docs/ui/components/ScoreCircle.ux 的 <template> 和 <style> -->
<!-- 前端自行添加 <script>： -->

<script>
export default {
  props: { score: { default: 0 } },
  computed: {
    color() { return this.score >= 80 ? '#ffd700' : '#ff9800' },
    label() { return this.score >= 80 ? '良好' : '一般' }
  }
}
</script>
```
