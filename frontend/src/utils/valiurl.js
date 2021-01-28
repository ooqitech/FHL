export default function isWhite (whiteList, path) {
  for (let i = 0; i < whiteList.length; i++) {
    const r = RegExp(whiteList[i])
    if (r.test(path)) {
      return true
    }
  }
  return false
}
