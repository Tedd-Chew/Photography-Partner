import fetch from '@system.fetch'
import file from '@system.file'
import { API_BASE_URL } from '../config'

var BASE_URL = API_BASE_URL

export function analyzePhoto(imagePath, mode, uid) {
  console.log('[analyze] start mode=' + mode + ' path=' + imagePath.substring(imagePath.lastIndexOf('/') + 1))

  return new Promise(function (resolve, reject) {
    file.readText({
      uri: imagePath,
      encoding: 'base64',
      success: function (data) {
        var body = JSON.stringify({
          image: data.text,
          mode: mode,
          uid: uid || 'device_unknown'
        })
        fetch.fetch({
          url: BASE_URL + '/api/analyze',
          method: 'POST',
          header: { 'Content-Type': 'application/json' },
          data: body,
          responseType: 'json',
          success: function (res) {
            var d = res.data || res
            if (d && d.ok) { resolve(d.data) }
            else { reject({ error: (d && d.error) || '分析失败' }) }
          },
          fail: function (err, code) { reject({ err: err, code: code }) }
        })
      },
      fail: function (err, code) {
        reject({ error: '文件读取失败 code=' + code })
      }
    })
  })
}

export function getUserInfo(uid) {
  return new Promise(function (resolve, reject) {
    fetch.fetch({
      url: BASE_URL + '/api/user/info?uid=' + uid,
      method: 'GET',
      responseType: 'json',
      success: function (res) { var d = res.data || res; if (d && d.ok) resolve(d.data); else reject({ error: (d && d.error) || '请求失败' }) },
      fail: function (err, code) { reject({ err: err, code: code }) }
    })
  })
}

export function getGallery(uid, page, size) {
  page = page || 1; size = size || 20
  return new Promise(function (resolve, reject) {
    fetch.fetch({
      url: BASE_URL + '/api/gallery?uid=' + uid + '&page=' + page + '&size=' + size,
      method: 'GET',
      responseType: 'json',
      success: function (res) {
        var d = res.data || res
        if (d && d.ok) {
          var items = d.data.items || []
          for (var i = 0; i < items.length; i++) {
            if (items[i].thumb_url && items[i].thumb_url.indexOf('/') === 0) {
              items[i].thumb_url = BASE_URL + items[i].thumb_url
            }
          }
          resolve(d.data)
        } else { reject({ error: (d && d.error) || '请求失败' }) }
      },
      fail: function (err, code) { reject({ err: err, code: code }) }
    })
  })
}

export function getGalleryDetail(id) {
  return new Promise(function (resolve, reject) {
    fetch.fetch({
      url: BASE_URL + '/api/gallery/' + id, method: 'GET', responseType: 'json',
      success: function (res) { var d = res.data || res; if (d && d.ok) resolve(d.data); else reject({ error: (d && d.error) || '请求失败' }) },
      fail: function (err, code) { reject({ err: err, code: code }) }
    })
  })
}
