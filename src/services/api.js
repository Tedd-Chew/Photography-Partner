import fetch from '@system.fetch'

const BASE = 'http://YOUR_SERVER_IP:8000/api'

async function request(method, path, body) {
  return new Promise((resolve, reject) => {
    fetch.fetch({
      url: BASE + path,
      method,
      header: { 'Content-Type': 'application/json' },
      data: body ? JSON.stringify(body) : '',
      responseType: 'json',
      success: (res) => resolve(res.data),
      fail: (err, code) => reject({ err, code })
    })
  })
}

// 上传文件（快应用 base64 方案）
async function upload(path, filePath, extra = {}) {
  // TODO: 前端图片压缩 + base64 → POST
}

// ====== 接口 ======

// 照片分析（三种模式）
export function analyzePhoto(imagePath, mode) {
  return upload('/analyze', imagePath, { mode })
}

// 用户信息
export function getUserInfo(uid) {
  return request('GET', `/user/info?uid=${uid}`)
}

// 历史列表（Gallery 页）
export function getGallery(uid, page = 1, size = 20) {
  return request('GET', `/gallery?uid=${uid}&page=${page}&size=${size}`)
}

// 历史详情
export function getGalleryDetail(id) {
  return request('GET', `/gallery/${id}`)
}
