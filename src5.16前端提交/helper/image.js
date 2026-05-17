const MAX_EDGE = 1024

export function compressImage(src, maxWidth = MAX_EDGE, quality = 0.85) {
  return new Promise((resolve) => {
    const image = require('@system.image')
    image.getImageInfo({
      src,
      success: (info) => {
        const width = info.width
        const height = info.height
        const maxSide = Math.max(width, height)

        if (maxSide <= maxWidth) {
          resolve(src)
          return
        }

        const ratio = maxWidth / maxSide
        const newWidth = Math.round(width * ratio)
        const newHeight = Math.round(height * ratio)

        image.compressImage({
          src,
          quality: Math.round(quality * 100),
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
