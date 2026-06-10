import fetch from '@system.fetch'
import uploadtask from '@system.uploadtask'
import { API_BASE_URL } from '../config'

var BASE_URL = API_BASE_URL

export function analyzePhoto(imagePath, mode, uid) {
  console.log('[analyzePhoto] start mode=' + mode + ' uid=' + uid)
  console.log('[analyzePhoto] imagePath=' + imagePath)

  return new Promise(function (resolve, reject) {
    uploadtask.uploadFile({
      url: BASE_URL + '/api/analyze',
      filePath: imagePath,
      name: 'image',
      formData: {
        mode: mode,
        uid: uid || 'device_unknown'
      },
      success: function (res) {
        console.log('[analyzePhoto] success statusCode=' + res.statusCode)
        console.log('[analyzePhoto] success raw=' + res.data)
        var d = JSON.parse(res.data)
        console.log('[analyzePhoto] parsed ok=' + d.ok + ' error=' + (d.error || 'none'))
        if (d && d.ok) {
          resolve(d.data)
        } else {
          reject({ error: (d && d.error) || '分析失败' })
        }
      },
      fail: function (err, code) {
        console.log('[analyzePhoto] fail code=' + code + ' err=' + JSON.stringify(err))
        reject({ error: '上传失败 code=' + code })
      }
    })
  })
}

export function getUserInfo(uid) {
  return new Promise(function (resolve, reject) {
    fetch.fetch({
      url: BASE_URL + '/user/info?uid=' + uid,
      method: 'GET',
      header: { 'Content-Type': 'application/json' },
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

export function getGallery(uid, page, size) {
  page = page || 1
  size = size || 20
  return new Promise(function (resolve, reject) {
    fetch.fetch({
      url: BASE_URL + '/gallery?uid=' + uid + '&page=' + page + '&size=' + size,
      method: 'GET',
      header: { 'Content-Type': 'application/json' },
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

export function getGalleryDetail(id) {
  return new Promise(function (resolve, reject) {
    fetch.fetch({
      url: BASE_URL + '/gallery/' + id,
      method: 'GET',
      header: { 'Content-Type': 'application/json' },
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
