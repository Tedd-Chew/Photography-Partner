import fetch from '@system.fetch'
import file from '@system.file'
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

function readFileAsBase64(fileUri) {
  return new Promise(function (resolve, reject) {
    file.readText({
      uri: fileUri,
      encoding: 'base64',
      success: function (data) {
        resolve(data.text)
      },
      fail: function (err, code) { reject({ err: err, code: code }) }
    })
  })
}

export function analyzePhoto(imagePath, mode, uid) {
  return readFileAsBase64(imagePath).then(function (base64Str) {
    return new Promise(function (resolve, reject) {
      fetch.fetch({
        url: BASE_URL + '/api/analyze',
        method: 'POST',
        header: { 'Content-Type': 'application/json' },
        data: JSON.stringify({
          image: base64Str,
          mode: mode,
          uid: uid || 'device_unknown'
        }),
        responseType: 'json',
        success: function (res) {
          var d = res.data
          if (d && d.ok) {
            resolve(d.data)
          } else {
            reject({ error: (d && d.error) || '分析失败' })
          }
        },
        fail: function (err, code) { reject({ err: err, code: code }) }
      })
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
