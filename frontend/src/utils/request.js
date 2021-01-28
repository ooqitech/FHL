import axios from 'axios'
import { MessageBox, Message } from 'element-ui'
import store from '@/store'
import router from '@/router'
import { getToken } from '@/utils/auth'

// create an axios instance
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API, // url = base url + request url
  // withCredentials: true, // send cookies when cross-domain requests
  timeout: 5000 // request timeout
})

// request interceptor
service.interceptors.request.use(
  config => {
    // do something before request is sent

    if (store.getters.token) {
      // let each request carry token
      // ['X-Token'] is a custom headers key
      // please modify it according to the actual situation
      const token = getToken()
      // console.log(token)
      config.headers['Authorization'] = 'Token ' + token
    }
    return config
  },
  error => {
    // do something with request error
    console.log(error) // for debug
    return Promise.reject(error)
  }
)

// response interceptor
service.interceptors.response.use(
  /**
   * If you want to get http information such as headers or status
   * Please return  response => response
   */

  /**
   * Determine the request status by custom code
   * Here is just an example
   * You can also judge the status by HTTP Status Code
   */
  response => {
    return response
    // if (response.status < 400) {
    //   // if the custom code is not 20000, it is judged as an error.
    //   return response
    // } else {
    //   switch (response.status) {
    //     case 401:
    //       store.dispatch('user/resetToken').then(() => {
    //         router.replace({
    //           path: '/login',
    //           query: { redirect: router.currentRoute.fullPath }
    //         })
    //       })
    //     case 403:
    //       router.push({
    //         path: '/403'
    //       })
    //   }
    // }
  },
  error => {
    console.log('err ' + error) // for debug
    if (error.response) {
      switch (error.response.status) {
        case 403:
          router.replace({
            path: '/403'
          })
          break
        case 401:
          store.dispatch('user/resetToken').then(() => {
            router.replace({
              path: '/login',
              query: { redirect: router.currentRoute.fullPath }
            })
          })
          break
        default:
          Message({
            type: 'error',
            message: error.response.data,
            duration: 2000
          })
          break

        // default:
        //   Message({
        //     type: 'error',
        //     message: error.response.data,
        //     duration: 3000
        //   })
        // return
      }
    }
    return Promise.reject(error)
  }
)

export default service
