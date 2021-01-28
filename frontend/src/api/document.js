import request from '@/utils/request'

export function getDocument (data) {
  return request({
    url: '/document/',
    method: 'get',
    params: data
  })
}

export function uploadDocument (data) {
  return request({
    url: '/document/',
    method: 'post',
    data
  })
}

export function deleteDocument (id) {
  return request({
    url: '/document/' + id + '/',
    method: 'delete',
  })
}

export function downloadDocument (id) {
  return request({
    url: '/document/' + id + '/download/',
    method: 'get',
  })
}

export function distributeDocument (id, data) {
  return request({
    url: '/document/' + id + '/distribute/',
    method: 'post',
    data
  })
}

export function restoreDocument (id, data) {
  return request({
    url: '/document/' + id + '/restore/',
    method: 'post',
    data
  })
}

export function getSyncFile (data) {
  return request({
    url: '/document/rsync/',
    method: 'get',
    params: data
  })
}

export function addSyncFile (data) {
  return request({
    url: '/document/rsync/',
    method: 'post',
    data
  })
}