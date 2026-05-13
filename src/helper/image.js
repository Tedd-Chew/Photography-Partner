// 前端图片压缩
// 在拍照后/选图后、上传前调用

export function compressImage(src, maxWidth = 1024, quality = 0.8) {
  // 快应用的图片处理 API — 待确认
  // 如果快应用支持 Canvas，用 Canvas 缩放
  // 否则后端压缩，前端直传
  return src
}

export function toBase64(filePath) {
  // 读取文件转 base64（如果需要）
}
