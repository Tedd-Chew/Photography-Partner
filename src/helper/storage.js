import storage from '@system.storage'

// 本地缓存 — 离线查看历史记录

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
      success: (data) => resolve(JSON.parse(data) || null),
      fail: () => resolve(null)
    })
  })
}

export function removeCache(key) {
  storage.delete({ key })
}
