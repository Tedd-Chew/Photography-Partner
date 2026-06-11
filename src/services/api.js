import fetch from '@system.fetch'
import uploadtask from '@system.uploadtask'
import { API_BASE_URL } from '../config'
import { compressImage } from '../helper/image'

var BASE_URL = API_BASE_URL

// ====== 第一步：上传图片（只上传，不调 AI，快速返回）======

export function uploadImage(imagePath) {
  console.log('[upload] start path=' + (imagePath || '').substring(0, 40))
  return new Promise(function (resolve, reject) {
    compressImage(imagePath).then(function (compressedPath) {
      console.log('[upload] compressed path=' + (compressedPath || '').substring(0, 40))

      var done = false
      var timer = setTimeout(function () {
        if (!done) { done = true; reject({ error: '上传超时，请检查网络后重试' }) }
      }, 30000)

      uploadtask.uploadFile({
        url: BASE_URL + '/api/images',
        filePath: compressedPath,
        name: 'file',
        formData: {},
        success: function (res) {
          if (done) return; done = true; clearTimeout(timer)
          console.log('[upload] ok status=' + res.statusCode)
          var d = res.data
          if (typeof d === 'string') { try { d = JSON.parse(d) } catch(e) {} }
          if (d && d.ok) resolve(d.data)
          else reject({ error: (d && d.error) || '上传失败' })
        },
        fail: function (err, code) {
          if (done) return; done = true; clearTimeout(timer)
          console.log('[upload] fail code=' + code + ' err=' + JSON.stringify(err))
          reject({ error: '上传失败 code=' + code + '，请检查网络后重试' })
        }
      })
    }).catch(function () {
      reject({ error: '图片处理失败' })
    })
  })
}

// ====== 第二步：触发 AI 分析（用 fetch，可以等更久）======

export function analyzePhoto(imageId, mode, uid, thumbUrl) {
  console.log('[analyze] start mode=' + mode + ' imageId=' + imageId)
  return new Promise(function (resolve, reject) {
    fetch.fetch({
      url: BASE_URL + '/api/analyze',
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: JSON.stringify({
        image_id: imageId,
        mode: mode,
        uid: uid || 'device_unknown',
        thumb_url: thumbUrl || ''
      }),
      responseType: 'json',
      timeout: 120000,
      success: function (res) {
        console.log('[analyze] ok')
        var d = res.data || res
        if (d && d.ok) resolve(d.data)
        else reject({ error: (d && d.error) || '分析失败' })
      },
      fail: function (err, code) {
        console.log('[analyze] fail code=' + code + ' err=' + JSON.stringify(err))
        reject({ error: '分析失败 code=' + code + '，请重试' })
      }
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
