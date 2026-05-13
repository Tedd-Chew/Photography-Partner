// 全局状态管理
// npm install qa-vuex --save（待快应用项目初始化后安装）

// 临时：用 app.ux 全局 data 替�� qa-vuex（先跑通再加）
export const store = {
  state: {
    user: {
      uid: '',
      level: 1,
      exp: 0,
      badges: [],
      streak: 0
    },
    camera: {
      scene: null,          // { label: '夜景', confidence: 0.9 }
      gridMode: 'thirds',   // 'off' | 'thirds' | 'golden' | 'crosshair'
      params: {
        shutter: null,
        iso: null,
        wb: null
      }
    },
    analysis: null,          // 当前分析结果
    history: []              // 历史摘要列表
  }
}
