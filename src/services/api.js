import fetch from '@system.fetch'
import uploadtask from '@system.uploadtask'
import { API_BASE_URL } from '../config'
import { compressImage } from '../helper/image'

var BASE_URL = API_BASE_URL

function doUpload(imagePath, mode, uid, resolve, reject) {
  var done = false
  var timer = setTimeout(function () {
    if (!done) { done = true; reject({ error: '上传超时(120s)，请检查网络后重试' }) }
  }, 120000)

  uploadtask.uploadFile({
    url: BASE_URL + '/api/analyze',
    filePath: imagePath,
    name: 'file',
    formData: { mode: mode, uid: uid || 'device_unknown' },
    success: function (res) {
      if (done) return; done = true; clearTimeout(timer)
      console.log('[analyze] upload ok status=' + res.statusCode)
      var d = res.data
      if (typeof d === 'string') { try { d = JSON.parse(d) } catch(e) {} }
      if (d && d.ok) resolve(d.data)
      else reject({ error: (d && d.error) || '分析失败' })
    },
    fail: function (err, code) {
      if (done) return; done = true; clearTimeout(timer)
      console.log('[analyze] upload fail code=' + code + ' err=' + JSON.stringify(err))
      reject({ error: '上传失败 code=' + code + '，请检查网络后重试' })
    }
  })
}

export function analyzePhoto(imagePath, mode, uid) {
  console.log('[analyze] start mode=' + mode + ' path=' + (imagePath || '').substring(0, 40))
  return new Promise(function (resolve, reject) {
    compressImage(imagePath).then(function (compressedPath) {
      console.log('[analyze] compressed path=' + (compressedPath || '').substring(0, 40))
      doUpload(compressedPath, mode, uid, resolve, reject)
    }).catch(function () {
      // 压缩失败不阻塞，用原图上传
      console.log('[analyze] compress failed, using original')
      doUpload(imagePath, mode, uid, resolve, reject)
    })
  })
}

export function getUserInfo(uid) {
  return new Promise(function (resolve, reject) {
    fetch.fetch({
      url: BASE_URL + '/api/user/info?uid=' + uid, method: 'GET', responseType: 'json',
      success: function (res) { var d = res.data || res; if (d && d.ok) resolve(d.data); else reject({ error: (d && d.error) || '请求失败' }) },
      fail: function (err, code) { reject({ err: err, code: code }) }
    })
  })
}

export function getGallery(uid, page, size) {
  page = page || 1; size = size || 20
  return new Promise(function (resolve, reject) {
    fetch.fetch({
      url: BASE_URL + '/api/gallery?uid=' + uid + '&page=' + page + '&size=' + size, method: 'GET', responseType: 'json',
      success: function (res) {
        var d = res.data || res
        if (d && d.ok) {
          var items = d.data.items || []
          for (var i = 0; i < items.length; i++) {
            if (items[i].thumb_url && items[i].thumb_url.indexOf('/') === 0)
              items[i].thumb_url = BASE_URL + items[i].thumb_url
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
    fetch.fetch({ url: BASE_URL + '/api/gallery/' + id, method: 'GET', responseType: 'json',
      success: function (res) { var d = res.data || res; if (d && d.ok) resolve(d.data); else reject({ error: (d && d.error) || '请求失败' }) },
      fail: function (err, code) { reject({ err: err, code: code }) }
    })
  })
}
