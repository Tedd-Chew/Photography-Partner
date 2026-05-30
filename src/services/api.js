import fetch from '@system.fetch'
import { compressImage, toBase64 } from '../helper/image'

const BASE_URL = 'http://10.0.2.2:8000'

function request(method, path, body) {
  return new Promise((resolve, reject) => {
    fetch.fetch({
      url: BASE_URL + path,
      method: method,
      header: { 'Content-Type': 'application/json' },
      data: body ? JSON.stringify(body) : '',
      responseType: 'json',
      success: (res) => {
        const d = res.data
        if (d && d.ok) {
          resolve(d.data)
        } else {
          reject({ error: (d && d.error) || '请求失败' })
        }
      },
      fail: (err, code) => reject({ err, code })
    })
  })
}

async function upload(path, filePath, extra = {}) {
  const compressed = compressImage(filePath, 1024, 0.8)
  const base64 = toBase64(compressed)

  const boundary = '----PhotographyPartner' + Date.now()
  const bodyParts = []
  bodyParts.push('--' + boundary)
  bodyParts.push('Content-Disposition: form-data; name="image"; filename="photo.jpg"')
  bodyParts.push('Content-Type: image/jpeg')
  bodyParts.push('')
  bodyParts.push(base64)

  const keys = Object.keys(extra)
  for (let i = 0; i < keys.length; i++) {
    bodyParts.push('--' + boundary)
    bodyParts.push('Content-Disposition: form-data; name="' + keys[i] + '"')
    bodyParts.push('')
    bodyParts.push(String(extra[keys[i]]))
  }
  bodyParts.push('--' + boundary + '--')

  const body = bodyParts.join('\r\n')

  return new Promise((resolve, reject) => {
    fetch.fetch({
      url: BASE + path,
      method: 'POST',
      header: { 'Content-Type': 'multipart/form-data; boundary=' + boundary },
      data: body,
      responseType: 'json',
      success: (res) => {
        const d = res.data
        if (d && d.ok) {
          resolve(d.data)
        } else {
          reject({ error: (d && d.error) || '上传失败' })
        }
      },
      fail: (err, code) => reject({ err, code })
    })
  })
}

export function analyzePhoto(imagePath, mode) {
  if (MOCK_MODE) {
    return new Promise((resolve) => {
      setTimeout(() => {
        if (mode === 'shooting') resolve(MOCK_SHOOTING)
        else if (mode === 'edit') resolve(MOCK_EDIT)
        else resolve(MOCK_SCORE)
      }, 1200)
    })
  }

  return uploadFile(imagePath, mode, getDeviceId())
}

export function getUserInfo(uid) {
  return request('GET', '/user/info?uid=' + uid)
}

export function getGallery(uid, page, size) {
  page = page || 1
  size = size || 20
  return request('GET', '/gallery?uid=' + uid + '&page=' + page + '&size=' + size)
}

export function getGalleryDetail(id) {
  return request('GET', '/gallery/' + id)
}
