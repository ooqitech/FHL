import request from '@/utils/request'

export function getUsers (data) {
  return request({
    url: '/account/users/',
    method: 'get',
    params: data
  })
}

export function AddUser (data) {
  return request({
    url: '/account/users/',
    method: 'post',
    data
  })
}

export function EditUser (id, data) {
  return request({
    url: '/account/users/' + id + '/',
    method: 'patch',
    data
  })
}

export function SetUserPassword (id, data) {
  return request({
    url: '/account/users/' + id + '/set_password/',
    method: 'put',
    data
  })
}

export function DeleteUser (id) {
  return request({
    url: '/account/users/' + id + '/',
    method: 'DELETE'
  })
}

export function getDepartments (data) {
  return request({
    url: '/account/departments/',
    method: 'get',
    params: data
  })
}

export function AddDepartment (data) {
  return request({
    url: '/account/departments/',
    method: 'post',
    data
  })
}

export function DeleteDepartment (id) {
  return request({
    url: '/account/departments/' + id + '/',
    method: 'DELETE'
  })
}

export function EditDepartment (id, data) {
  return request({
    url: '/account/departments/' + id + '/',
    method: 'patch',
    data
  })
}

export function getPermissions (data) {
  return request({
    url: '/account/permissions/',
    method: 'get',
    params: data
  })
}

export function AddPermissions (data) {
  return request({
    url: '/account/permissions/',
    method: 'post',
    data
  })
}

export function DeletePermissions (id) {
  return request({
    url: '/account/permissions/' + id + '/',
    method: 'DELETE'
  })
}

export function getGroups (data) {
  return request({
    url: '/account/group/',
    method: 'get',
    params: data
  })
}

export function AddGroup (data) {
  return request({
    url: '/account/group/',
    method: 'post',
    data
  })
}

export function EditGroup (id, data) {
  return request({
    url: '/account/group/' + id + '/',
    method: 'patch',
    data
  })
}

export function DeleteGroup (id) {
  return request({
    url: '/account/group/' + id + '/',
    method: 'DELETE'
  })
}

export function getAction (data) {
  return request({
    url: '/account/action/',
    method: 'get',
    params: data
  })
}