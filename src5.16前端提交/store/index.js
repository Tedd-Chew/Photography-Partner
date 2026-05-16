const state = {
  user: {
    uid: '',
    nickname: '',
    level: 1,
    exp: 0,
    badges: [],
    totalAnalyses: 0
  },

  camera: {
    scene: null,
    gridMode: 'thirds',
    params: null
  },

  analysis: null,

  analysisMode: 'score',

  history: [],

  currentImage: null,

  loading: false
}

function setUser(data) {
  Object.assign(state.user, data)
}

function setCamera(data) {
  Object.assign(state.camera, data)
}

function setAnalysis(data) {
  state.analysis = data
}

function setAnalysisMode(mode) {
  state.analysisMode = mode
}

function setLoading(val) {
  state.loading = val
}

function setCurrentImage(uri) {
  state.currentImage = uri
}

function setHistory(list) {
  state.history = list
}

function addBadge(badge) {
  if (badge && !state.user.badges.includes(badge)) {
    state.user.badges.push(badge)
  }
}

function addExp(amount) {
  state.user.exp += amount
  if (state.user.exp >= 1600) {
    state.user.level = 6
  } else if (state.user.exp >= 1000) {
    state.user.level = 5
  } else if (state.user.exp >= 600) {
    state.user.level = 4
  } else if (state.user.exp >= 300) {
    state.user.level = 3
  } else if (state.user.exp >= 100) {
    state.user.level = 2
  }
}

function clearAnalysis() {
  state.analysis = null
  state.currentImage = null
}

export const store = {
  state,
  setUser,
  setCamera,
  setAnalysis,
  setAnalysisMode,
  setLoading,
  setCurrentImage,
  setHistory,
  addBadge,
  addExp,
  clearAnalysis
}
