import fetch from '@system.fetch'
import request from '@system.request'
import { API_BASE_URL } from '../config'

var BASE_URL = API_BASE_URL

function jsonRequest(method, path, body) {
  return new Promise(function (resolve, reject) {
    fetch.fetch({
      url: BASE_URL + path,
      method: method,
      header: { 'Content-Type': 'application/json' },
      data: body ? JSON.stringify(body) : '',
      responseType: 'json',
      success: function (res) {
        var d = res.data
        if (d && d.ok) {
          resolve(d.data)
        } else {
          reject({ error: (d && d.error) || '请求失败' })
        }
      },
      fail: function (err, code) { reject({ err: err, code: code }) }
    })
  })
}

export function analyzePhoto(imagePath, mode, uid) {
  return new Promise(function (resolve, reject) {
    request.upload({
      url: BASE_URL + '/api/analyze',
      filePath: imagePath,
      name: 'image',
      formData: {
        mode: mode,
        uid: uid || 'device_unknown'
      },
      success: function (res) {
        try {
          var d = JSON.parse(res.data)
          if (d && d.ok) {
            resolve(d.data)
          } else {
            reject({ error: (d && d.error) || '分析失败' })
          }
        } catch (e) {
          reject({ error: '服务器返回数据格式错误' })
        }
      },
      fail: function (err, code) {
        reject({ err: err, code: code })
      }
    })
  })
}

export function getUserInfo(uid) {
  return jsonRequest('GET', '/user/info?uid=' + uid)
}

export function getGallery(uid, page, size) {
  page = page || 1
  size = size || 20
  return jsonRequest('GET', '/gallery?uid=' + uid + '&page=' + page + '&size=' + size)
}

export function getGalleryDetail(id) {
  return jsonRequest('GET', '/gallery/' + id)
}
