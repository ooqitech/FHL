import request from '@/utils/request'

export function getCmdb (data) {
  return request({
    url: '/cmdb/ecs/',
    method: 'get',
    params: data
  })
}

export function getEcs (data) {
  return request({
    url: '/cmdb/ecs_list/',
    method: 'get',
    params: data
  })
}

export function getTemplate (data) {
  return request({
    url: '/cmdb/ecs/template/',
    method: 'get',
    params: data,
    responseType: 'blob'
  })
}

export function getHostByAppName (data) {
  return request({
    url: '/cmdb/ecs/app_to_host/',
    method: 'get',
    params: data
  })
}

export function getDatabaseFull (data) {
  return request({
    url: '/cmdb/database/full/',
    method: 'get',
    params: data
  })
}

export function unBindEcs (id) {
  return request({
    url: '/cmdb/ecs/' + id + '/unbind/',
    method: 'patch'
  })
}

export function getEcsIdle () {
  return request({
    url: '/cmdb/ecs/idle/',
    method: 'get'
  })
}

export function appbindEcs (data) {
  return request({
    url: '/cmdb/ecs/batch_bind/',
    method: 'patch',
    data
  })
}

export function bindsEcs (data) {
  return request({
    url: '/cmdb/ecs/binds/',
    method: 'patch',
    data
  })
}

export function getStaff (data) {
  return request({
    url: '/cmdb/staff/',
    method: 'get',
    params: data
  })
}

export function AddStaff (data) {
  return request({
    url: '/cmdb/staff/',
    method: 'post',
    data
  })
}

export function DeleteStaff (id) {
  return request({
    url: '/cmdb/staff/' + id + '/',
    method: 'DELETE'
  })
}