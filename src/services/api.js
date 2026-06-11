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

// ====== 第二步：触发 AI 分析（POST 启动 + GET 轮询，不超时）======

export function analyzePhoto(imageId, mode, uid, thumbUrl) {
  console.log('[analyze] start mode=' + mode + ' imageId=' + imageId)
  return new Promise(function (resolve, reject) {
    // 发 POST 启动分析，立即拿到 task_id
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
      success: function (res) {
        var d = res.data || res
        if (!d || !d.ok || !d.data || !d.data.task_id) {
          reject({ error: (d && d.error) || '启动分析失败' })
          return
        }
        var taskId = d.data.task_id
        console.log('[analyze] taskId=' + taskId + ', start polling...')
        poll(taskId, resolve, reject)
      },
      fail: function (err, code) {
        reject({ error: '启动分析失败 code=' + code })
      }
    })
  })
}

function poll(taskId, resolve, reject) {
  var count = 0
  var maxPolls = 60  // 60 * 2s = 120s

  function tick() {
    count++
    fetch.fetch({
      url: BASE_URL + '/api/analyze/' + taskId,
      method: 'GET',
      responseType: 'json',
      success: function (res) {
        var r = res.data || res
        if (!r || !r.ok) {
          if (r && r.error) { reject({ error: r.error }); return }
          // 网络小波动，继续
          if (count >= maxPolls) { reject({ error: '分析超时，请重试' }); return }
          setTimeout(tick, 2000)
          return
        }
        if (r.data && r.data.status === 'processing') {
          console.log('[poll] ' + count + ' processing...')
          if (count >= maxPolls) { reject({ error: '分析超时，请重试' }); return }
          setTimeout(tick, 2000)
          return
        }
        // done — data 直接就是分析结果
        console.log('[poll] done at ' + count)
        resolve(r.data)
      },
      fail: function () {
        console.log('[poll] ' + count + ' network fail, retry...')
        if (count >= maxPolls) { reject({ error: '分析超时，请重试' }); return }
        setTimeout(tick, 2000)
      }
    })
  }

  tick()
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
