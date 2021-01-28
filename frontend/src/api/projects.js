import request from '@/utils/request'

export function getAllProject () {
  return request({
    url: '/projects/full/',
    method: 'get'
  })
}

export function getEmployee (data) {
  return request({
    url: '/projects/sre/employee/',
    method: 'get',
    params: data
  })
}

export function addEmployee (data) {
  return request({
    url: '/projects/sre/employee/',
    method: 'post',
    data
  })
}

export function editEmployee (data) {
  return request({
    url: '/projects/sre/employee/',
    method: 'put',
    data
  })
}

export function deleteEmployee (data) {
  return request({
    url: '/projects/sre/employee/',
    method: 'delete',
    data
  })
}

export function getProjects (data) {
  return request({
    url: '/projects/index/',
    method: 'get',
    params: data
  })
}

export function getProjectById (id) {
  return request({
    url: '/projects/index/' + id + '/',
    method: 'get'
  })
}

export function AddProjects (data) {
  return request({
    url: '/projects/index/',
    method: 'POST',
    data
  })
}

export function editProjects (id, data) {
  return request({
    url: '/projects/index/' + id + '/',
    method: 'put',
    data
  })
}

export function deleteProject (id) {
  return request({
    url: '/projects/index/' + id + '/',
    method: 'delete'
  })
}

export function getSreBusiness (data) {
  return request({
    url: '/projects/index/sre_business/',
    method: 'get',
    params: data
  })
}