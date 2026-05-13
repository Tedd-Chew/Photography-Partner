# Photography-Partner
一个提高你摄影水平的ai摄影助手
# Git 协作极简规范（4人小团队专用）
> **一句话核心：先拉再写，写完再拉，分支干活，PR合并**
> 
> 所有人严格遵守这16个字，99%不会有代码冲突。

---

## 🚫 3条铁律（违反必出问题）
1. 永远不要直接在 `main` 分支写代码
2. 写代码前先拉，提交前再拉
3. 一个分支只做一件事，做完就删

---

## 🔄 每日5步流程（复制粘贴就行）
### 1. 早上开工（必做）
```bash
git checkout main
git pull origin main
git checkout -b feature/你的昵称-今天做什么
```
✅ 示例：`git checkout -b feature/小明-产品搜索框`

### 2. 写代码（每2-3小时一次）
```bash
git add 你改的文件
git commit -m "类型: 做了什么"
```
✅ 示例：`git commit -m "feat: 完成搜索框输入功能"`

### 3. 准备提交前（最关键）
```bash
git pull origin main
```
- 没冲突：继续下一步
- 有冲突：打开文件改好，再执行 `git add . && git commit -m "merge: 解决冲突"`

### 4. 推送并合并
```bash
git push origin 你的分支名
```
然后去GitHub点 **Compare & pull request** → 喊一个人看一眼 → 合并

### 5. 清理收尾（必做）
```bash
git checkout main
git pull origin main
git branch -d 你的分支名
```

---

## ✍️ 提交信息怎么写
只用这6个类型，足够用了：
- `feat:` 加新功能
- `fix:` 修bug
- `docs:` 改文档
- `style:` 改格式（缩进、空格）
- `refactor:` 改代码结构
- `chore:` 装依赖、改配置

✅ 好：`git commit -m "fix: 修复图片不显示问题"`  
❌ 坏：`git commit -m "更新"`

---

## ❌ 绝对不能做的事
1. 不要用 `git push -f` 强制推送到main分支
2. 不要一个分支写超过3天
3. 不要一次提交10个以上文件
4. 不要改别人正在写的文件，要改先在群里说一声
5. 不要把密码、密钥提交到Git

---

## 📋 常用命令速查
```bash
git status          # 看自己改了什么
git branch          # 看所有分支
git log --oneline   # 看提交历史
git reset --soft HEAD~1  # 撤销最后一次提交（保留代码）
git checkout .      # 放弃本地所有修改
```
