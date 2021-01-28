import request from '@/utils/request'

export function getAppList() {
  return request({
    url: '/ams/app_list/',
    method: 'get'
  })
}

export function getDatabase() {
  return request({
    url: '/ams/database/',
    method: 'get'
  })
}
