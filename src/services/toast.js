import prompt from '@system.prompt'

export function showToast(text, duration) {
  prompt.showToast({
    message: text,
    duration: duration || 2000
  })
}

export function showSuccess(text) {
  showToast('✓ ' + (text || '操作成功'))
}

export function showError(text) {
  showToast('✗ ' + (text || '操作失败'))
}
