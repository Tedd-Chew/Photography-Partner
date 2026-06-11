const MAX_EDGE = 800
const JPEG_QUALITY = 75  // 和缩略图一致，大幅减小文件体积

export function compressImage(src, maxWidth = MAX_EDGE, quality = JPEG_QUALITY) {
  return new Promise((resolve) => {
    const image = require('@system.image')
    image.getImageInfo({
      src,
      success: (info) => {
        const width = info.width
        const height = info.height
        const maxSide = Math.max(width, height)
        const ratio = maxSide > maxWidth ? maxWidth / maxSide : 1
        const newWidth = Math.round(width * ratio)
        const newHeight = Math.round(height * ratio)

        image.compressImage({
          src,
          quality: quality,  // 0-100
          width: newWidth,
          height: newHeight,
          success: (res) => resolve(res.uri),
          fail: () => resolve(src)
        })
      },
      fail: () => resolve(src)
    })
  })
}

export function toBase64(filePath) {
  return new Promise((resolve, reject) => {
    const file = require('@system.file')
    file.readText({
      uri: filePath,
      encoding: 'base64',
      success: (res) => resolve(res.text),
      fail: reject
    })
  })
}
