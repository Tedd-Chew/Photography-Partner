import fetch from '@system.fetch'

const BASE_URL = 'http://10.0.2.2:8000'

const MOCK_MODE = true

const MOCK_SCORE = {
  ok: true,
  data: {
    id: 'mock_001',
    mode: 'score',
    thumb_url: '',
    score: 78,
    comment: '这张照片整体不错！构图把人物放在三分线位置很舒服。可以改进的是背景稍微过曝了，下次试试降低曝光补偿。色温可以往暖色调方向微调，让肤色更自然。',
    exp_gained: 25,
    level_up: null,
    badge_unlocked: ['首战告捷']
  }
}

const MOCK_EDIT = {
  ok: true,
  data: {
    id: 'mock_002',
    mode: 'edit',
    thumb_url: '',
    advice: '这张照片可以先调一下色温，往暖色偏一点约 5500K，让肤色看起来更自然。然后亮度面板把曝光 +0.3，阴影 +15 提亮暗部。清晰度这块不用动，拍得挺锐的。最后可以加一点自然饱和度 +8，画面会更生动。整体来说基础底子不错，两三步就能调出感觉。'
  }
}

const MOCK_SHOOTING = {
  ok: true,
  data: {
    id: 'mock_003',
    mode: 'shooting',
    thumb_url: '',
    scene: '夜景人像',
    camera_params: {
      shutter: '1/30',
      iso: '800',
      aperture: 'f/2.8',
      wb: '4000K',
      focus: '人物面部单点对焦'
    },
    composition_tips: [
      '人物置于画面右侧三分线，左侧留出城市灯光背景',
      '利用路边栏杆作为引导线，将视线引向人物'
    ],
    lighting_advice: '利用街道暖色灯光作为主光源，避免头顶路灯直射导致面部过曝',
    extra_tips: '建议使用三脚架，夜间慢速快门避免手抖'
  }
}

const MOCK_USER = {
  ok: true,
  data: {
    uid: 'demo_user_001',
    nickname: '摄影爱好者',
    level: 3,
    exp: 420,
    badges: ['高分达人', '首战告捷'],
    total_analyses: 23
  }
}

const MOCK_GALLERY = {
  ok: true,
  data: {
    items: [
      {
        id: 'mock_001',
        mode: 'score',
        thumb_url: '',
        result_json: MOCK_SCORE.data,
        created_at: '2026-05-14 10:30:00'
      },
      {
        id: 'mock_002',
        mode: 'edit',
        thumb_url: '',
        result_json: MOCK_EDIT.data,
        created_at: '2026-05-13 18:20:00'
      },
      {
        id: 'mock_003',
        mode: 'shooting',
        thumb_url: '',
        result_json: MOCK_SHOOTING.data,
        created_at: '2026-05-12 21:00:00'
      }
    ],
    total: 3,
    page: 1
  }
}

function getDeviceId() {
  try {
    return device.getInfoSync().deviceId || 'demo_device_001'
  } catch (e) {
    return 'demo_device_001'
  }
}

function request(method, path, body) {
  return new Promise((resolve, reject) => {
    fetch.fetch({
      url: BASE_URL + path,
      method: method,
      header: { 'Content-Type': 'application/json' },
      data: body ? JSON.stringify(body) : '',
      responseType: 'json',
      success: (res) => resolve(res.data),
      fail: (err, code) => reject({ err, code })
    })
  })
}

function uploadFile(filePath, mode, uid) {
  return new Promise((resolve, reject) => {
    fetch.upload({
      url: BASE_URL + '/api/analyze',
      filePath: filePath,
      name: 'image',
      formData: { mode: mode, uid: uid },
      success: (res) => {
        try {
          const data = JSON.parse(res.data)
          resolve(data)
        } catch (e) {
          reject(new Error('解析响应失败'))
        }
      },
      fail: (err) => reject(err)
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
  if (MOCK_MODE) {
    return new Promise((resolve) => {
      setTimeout(() => resolve(MOCK_USER), 300)
    })
  }

  const deviceId = uid || getDeviceId()
  return request('GET', `/api/user/info?uid=${deviceId}`)
}

export function getGallery(uid, page = 1, size = 20) {
  if (MOCK_MODE) {
    return new Promise((resolve) => {
      setTimeout(() => resolve(MOCK_GALLERY), 400)
    })
  }

  const deviceId = uid || getDeviceId()
  return request('GET', `/api/gallery?uid=${deviceId}&page=${page}&size=${size}`)
}

export function getGalleryDetail(id) {
  if (MOCK_MODE) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const found = MOCK_GALLERY.data.items.find((item) => item.id === id)
        if (found) {
          resolve({ ok: true, data: found.result_json })
        } else {
          resolve({ ok: false, error: '记录不存在' })
        }
      }, 300)
    })
  }

  return request('GET', `/api/gallery/${id}`)
}
