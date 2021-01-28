import request from '@/utils/request'

export function login (data) {
  return request({
    url: '/api-token-auth/',
    method: 'post',
    data
  })
}