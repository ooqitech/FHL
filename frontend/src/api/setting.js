import request from '@/utils/request'

export function getAliyunConfig () {
  return request({
    url: '/account/config/aliyun/',
    method: 'get'
  })
}

export function getSystem () {
  return request({
    url: '/account/config/system/',
    method: 'get'
  })
}

export function AddAliyun (data) {
  return request({
    url: '/account/config/aliyun/',
    method: 'post',
    data
  })
}

export function AddSystem (data) {
  return request({
    url: '/account/config/system/',
    method: 'post',
    data
  })
}

export function DeleteAliyun (id) {
  return request({
    url: '/account/config/aliyun/' + id + '/',
    method: 'DELETE'
  })
}

export function AddSystemSetting (data) {
  return request({
    url: '/account/config/system/',
    method: 'post',
    data
  })
}

export function getSshConfig () {
  return request({
    url: '/account/config/ssh/',
    method: 'get'
  })
}


export function AddSshConfig (data) {
  return request({
    url: '/account/config/ssh/',
    method: 'post',
    data
  })
}

export function DeleteSshConfig (id) {
  return request({
    url: '/account/config/ssh/' + id + '/',
    method: 'DELETE'
  })
}