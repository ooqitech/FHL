const getters = {
  sidebar: state => state.app.sidebar,
  device: state => state.app.device,
  token: state => state.user.token,
  avatar: state => state.user.avatar,
  name: state => state.user.name,
  title: state => state.settings.title || localStorage.getItem('title'),
  logoimg: state => state.settings.logoimg || localStorage.getItem('logoimg')
}
export default getters
