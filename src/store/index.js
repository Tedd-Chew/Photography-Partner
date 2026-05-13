// 全局状态管理
export const store = {
  state: {
    user: {
      uid: '',
      level: 1,
      exp: 0,
      badges: []
    },
    // 当前分析结果（Result 页用）
    analysis: null,
    // 分析历史缓存（Gallery 页用，本地存满再从后端拉）
    history: []
  }
}
