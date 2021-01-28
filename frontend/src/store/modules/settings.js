import defaultSettings from '@/settings'
import { getSystem } from '@/api/setting'

const { showSettings, fixedHeader, sidebarLogo } = defaultSettings

const state = {
  showSettings: showSettings,
  fixedHeader: fixedHeader,
  sidebarLogo: sidebarLogo,
  title: '',
  logoimg: '',
}

const mutations = {
  CHANGE_SETTING: (state, { key, value }) => {
    if (state.hasOwnProperty(key)) {
      state[key] = value
    }
  },
  CHANGE_TITLE: (state, title) => {
    state.title = title
    localStorage.setItem('title', title)
  },
  CHANGE_LOGO: (state, logo) => {
    state.logoimg = logo
    localStorage.setItem('logoimg', logo)
  }
}

const actions = {
  getSystem ({ commit }) {
    return new Promise((resolve, reject) => {
      getSystem()
        .then(response => {
          const { data } = response
          console.log(data)
          if (data.results.length > 0) {
            commit('CHANGE_TITLE', data.results[0].name)
            commit('CHANGE_LOGO', data.results[0].logo)
          }
          resolve()
        })
        .catch(error => {
          reject(error)
        })
    })
  },
  changeSetting ({ commit }, data) {
    commit('CHANGE_SETTING', data)
  },
  clearSystem ({ commit }) {
    return new Promise((resolve, reject) => {
      commit('CHANGE_TITLE', '')
      commit('CHANGE_LOGO', '')
      resolve()
    })
  }

}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}

