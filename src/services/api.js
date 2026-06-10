import fetch from '@system.fetch'
import { compressImage, toBase64 } from '../helper/image'
import { API_BASE_URL } from '../config'

const BASE_URL = API_BASE_URL

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
  const compressedUri = await compressImage(filePath, 1024, 0.8)
  const base64 = await toBase64(compressedUri)

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
      url: BASE_URL + path,
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

export function analyzePhoto(imagePath, mode, uid) {
  return upload('/api/analyze', imagePath, { mode, uid })
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
