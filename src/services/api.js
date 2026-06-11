import fetch from '@system.fetch'
import uploadtask from '@system.uploadtask'
import { API_BASE_URL } from '../config'

var BASE_URL = API_BASE_URL

export function analyzePhoto(imagePath, mode, uid) {
  console.log('[analyze] start mode=' + mode + ' path=' + imagePath.substring(imagePath.lastIndexOf('/') + 1))

  return new Promise(function (resolve, reject) {
    uploadtask.uploadFile({
    url: BASE_URL + '/api/analyze?mode=' + mode + '&uid=' + (uid || 'device_unknown'),
    filePath: imagePath,
    name: 'image',
    formData: { mode: mode, uid: uid || 'device_unknown' },
    success: function (res) {
      var d = res.data
      if (typeof d === 'string') {
        try { d = JSON.parse(d) } catch (e) {
          console.log('[analyze] parse fail raw=' + d.substring(0, 100))
          reject({ error: '服务器返回异常' }); return
        }
      }
      console.log('[analyze] ok=' + d.ok + ' error=' + (d.error || 'none'))
      if (d && d.ok) { resolve(d.data) }
      else { reject({ error: (d && d.error) || '分析失败' }) }
    },
    fail: function (err, code) {
      console.log('[analyze] fail code=' + code + ' err=' + JSON.stringify(err))
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
      success: function (res) { var d = res.data; if (d && d.ok) resolve(d.data); else reject({ error: (d && d.error) || '请求失败' }) },
      fail: function (err, code) { reject({ err: err, code: code }) }
    })
  })
}

export function getGallery(uid, page, size) {
  page = page || 1
  size = size || 20
  return new Promise(function (resolve, reject) {
    fetch.fetch({
      url: BASE_URL + '/api/gallery?uid=' + uid + '&page=' + page + '&size=' + size,
      method: 'GET',
      header: { 'Content-Type': 'application/json' },
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
      url: BASE_URL + '/api/gallery/' + id,
      method: 'GET',
      header: { 'Content-Type': 'application/json' },
      responseType: 'json',
      success: function (res) { var d = res.data; if (d && d.ok) resolve(d.data); else reject({ error: (d && d.error) || '请求失败' }) },
      fail: function (err, code) { reject({ err: err, code: code }) }
    })
  })
}
