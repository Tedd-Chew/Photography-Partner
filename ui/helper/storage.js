import storage from '@system.storage'

const CACHE_KEY = 'photography_history_cache'
const UID_KEY = 'photography_uid'

export function saveCache(key, data) {
  storage.set({
    key,
    value: JSON.stringify(data),
    success: () => {},
    fail: (err) => console.log('cache save failed', err)
  })
}

export function getCache(key) {
  return new Promise((resolve) => {
    storage.get({
      key,
      success: (data) => {
        try {
          resolve(JSON.parse(data) || null)
        } catch (e) {
          resolve(null)
        }
      },
      fail: () => resolve(null)
    })
  })
}

export function removeCache(key) {
  storage.delete({ key })
}

export function saveToHistoryCache(data) {
  getCache(CACHE_KEY).then((raw) => {
    let list = []
    if (raw) {
      try {
        list = JSON.parse(raw)
      } catch (e) {
        list = []
      }
    }
    list.unshift(data)
    if (list.length > 30) {
      list = list.slice(0, 30)
    }
    saveCache(CACHE_KEY, list)
  })
}

export function getCachedHistory() {
  return getCache(CACHE_KEY).then((raw) => {
    if (!raw) return []
    try {
      return JSON.parse(raw) || []
    } catch (e) {
      return []
    }
  })
}

export function clearHistoryCache() {
  removeCache(CACHE_KEY)
}

export function getUid() {
  return getCache(UID_KEY).then((uid) => {
    if (uid) return uid
    const newUid = 'user_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8)
    saveCache(UID_KEY, newUid)
    return newUid
  })
}
