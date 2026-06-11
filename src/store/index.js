import { getCache, saveCache } from '../helper/storage'

export const store = {
  state: {
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
      params: { shutter: null, iso: null, aperture: null, wb: null, focus: null }
    },

    analysis: null,
    localUri: '',

    history: []
  },

  setUser(data) {
    Object.assign(this.state.user, data)
    saveCache('user', this.state.user)
  },

  setCameraParams(scene, params) {
    this.state.camera.scene = scene
    this.state.camera.params = params
  },

  setAnalysis(data) {
    this.state.analysis = data
    saveCache('analysis', data)
    if (data.exp_gained) {
      this.state.user.exp += data.exp_gained
    }
    if (data.level_up && data.level_up.new_level) {
      this.state.user.level = data.level_up.new_level
    }
    if (data.badge_unlocked && data.badge_unlocked.length) {
      const badges = this.state.user.badges
      for (let i = 0; i < data.badge_unlocked.length; i++) {
        if (badges.indexOf(data.badge_unlocked[i]) === -1) {
          badges.push(data.badge_unlocked[i])
        }
      }
    }
    this.state.user.totalAnalyses += 1
    saveCache('user', this.state.user)
  },

  setHistory(list) {
    this.state.history = list
  },

  clearAnalysis() {
    this.state.analysis = null
  }
}

