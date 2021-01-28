<template>
  <div class="app-container">
    <el-dialog title="添加部门"
               :visible.sync="centerDialogVisible"
               width="30%"
               center
               destroy-on-close
               @close="resetForm('form')">
      <div class="dialog-form">
        <el-form ref="form"
                 :model="form"
                 :rules="dialogRules"
                 label-width="100px"
                 class="dialogbody">
          <el-form-item label="部门名称"
                        prop="name">
            <el-input v-model="form.name"
                      style="width: 71%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item label="部门全称"
                        prop="detail">
            <el-input v-model="form.detail"
                      style="width: 71%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item label="部门邮箱"
                        prop="email">
            <el-input v-model="form.email"
                      style="width: 71%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item class="config_element"
                        label="部门权限"
                        prop="permission">
            <el-select v-model="form.permission"
                       filterable
                       multiple
                       placeholder="请选择"
                       style="width: 71%">
              <el-option v-for="item in allPermissions"
                         :key="item.id"
                         :label="item.name"
                         :value="item.id"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="备注"
                        prop="desc">
            <el-input v-model="form.desc"
                      style="width: 71%"
                      autocomplete="off"></el-input>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer"
            class="dialog-footer">
        <el-button @click="resetForm('form')">取 消</el-button>
        <el-button type="primary"
                   @click="AddDepartmentForm('form')">确 定</el-button>
      </span>
    </el-dialog>

    <el-form :inline="true"
             class="demo-form-inline">
      <el-form-item>
        <el-button type="primary"
                   @click="centerDialogVisible = true">添加部门</el-button>
      </el-form-item>
    </el-form>

    <el-table v-loading="listLoading"
              :data="list"
              element-loading-text="Loading"
              border
              fit
              highlight-current-row>
      <el-table-column align="center"
                       label="ID"
                       width="95">
        <template slot-scope="scope">
          {{ scope.row.id }}
        </template>
      </el-table-column>
      <el-table-column label="部门名称"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column label="部门全称"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.detail }}
        </template>
      </el-table-column>
      <el-table-column label="部门邮箱"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.email }}
        </template>
      </el-table-column>
      <el-table-column label="备注"
                       align="center">
        <template slot-scope="scope">
          {{ checkDesc(scope.row.desc) }}
        </template>
      </el-table-column>
      <el-table-column align="center"
                       prop="created_at"
                       label="操作"
                       width="200">
        <template slot-scope="scope">
          <el-button size="mini"
                     type="primary"
                     icon="el-icon-edit"
                     round
                     @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button v-if="scope.row.name === 'admin'"
                     size="mini"
                     icon="el-icon-delete"
                     round
                     disabled>删除</el-button>
          <el-button v-else
                     size="mini"
                     type="danger"
                     icon="el-icon-delete"
                     round
                     @click="handleDelete(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination class="pagination"
                   v-if="total > 0"
                   @size-change="handleSizeChange"
                   @current-change="handleCurrentChange"
                   :current-page="currentPage"
                   :page-sizes="[10, 20, 50, 100]"
                   :page-size="pageSize"
                   layout="total, sizes, prev, pager, next, jumper"
                   :total="total" />
    <el-dialog title="部门编辑"
               :visible.sync="diaIsShow"
               class="diaForm"
               width="30%">
      <el-form ref="diaForm"
               :model="editformData"
               :rules="dialogRules"
               label-width="100px">
        <el-form-item label="部门名称"
                      prop="name">
          <el-input type="text"
                    v-model="editformData.name"
                    style="width: 71%"
                    disabled></el-input>
        </el-form-item>
        <el-form-item label="部门全称"
                      prop="detail">
          <el-input v-model="editformData.detail"
                    style="width: 71%"
                    autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="部门邮箱"
                      prop="email">
          <el-input v-model="editformData.email"
                    style="width: 71%"
                    autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item class="config_element"
                      label="部门权限"
                      prop="permission">
          <el-select v-model="editformData.permission"
                     filterable
                     multiple
                     placeholder="请选择"
                     style="width: 71%">
            <el-option v-for="item in allPermissions"
                       :key="item.id"
                       :label="item.name"
                       :value="item.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="备注"
                      prop="desc">
          <el-input v-model="form.desc"
                    style="width: 71%"
                    autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary"
                     @click="changeTab('diaForm', editType )">确认</el-button>
          <el-button @click="diaIsShow = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script>
import { getDepartments, AddDepartment, EditDepartment, DeleteDepartment, getPermissions } from '@/api/account.js'
import { constants } from 'fs';
import { setTimeout } from 'timers';
export default {
  data () {
    return {
      list: null,
      listLoading: true,
      diaIsShow: false,
      editformData: {},
      editType: '',
      dialogRules: {
        name: [{ required: true, trigger: 'blur', message: '部门名称不能为空' }],
        detail: [{ required: true, trigger: 'blur', message: '部门全称不能为空' }],
        email: [{ required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }],
        permission: [{ required: true, trigger: 'blur', message: '权限不能为空' }],
      },
      // Rules: {
      //   username: [{ required: true, trigger: 'blur', message: '用户名不能为空' }],
      //   email: [{ required: true, message: '请输入邮箱地址', trigger: 'blur' },
      //   { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }],
      //   phone: [{ required: true, validator: checkPhone, trigger: 'blur' }],
      //   department: [{ required: true, trigger: 'blur', message: '部门不能为空' }],
      // },
      form: {
        name: '',
        detail: '',
        email: '',
        permission: [],
        desc: ''
      },
      pickerOptions: {
        disabledDate (time) {
          return time.getTime() > Date.now()
        }
      },
      // value: true,
      centerDialogVisible: false,
      total: 0,
      currentPage: 1,
      pageSize: 10,
      allPermissions: [],
      PermissionsObj: {},
      rowIndex: 0
      ,
    }
  },
  created () {
    this.fetchData()
    this.fetchPermission()
  },
  methods: {
    fetchData () {
      this.listLoading = true
      getDepartments().then(response => {
        this.list = response.data.results
        this.total = response.data.count
        this.listLoading = false
      }).catch(error => {
        console.log(error)
      })
    },
    fetchPermission () {
      getPermissions().then(response => {
        let results = response.data.results
        for (let i in results) {
          this.allPermissions.push({
            id: results[i].id,
            name: results[i].name
          })
          this.PermissionsObj[results[i].id] = results[i].name
        }
      }).catch(error => {
        console.log(error)
      })
    },
    handleDelete (index, row) {
      this.$confirm('你真的要删除 ' + row.name + ' 么？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        DeleteDepartment(row.id).then(response => {
          for (var i = 0; i < this.list.length; i++) {
            if (this.list[i].id === row.id) {
              this.list.splice(i, 1)
            }
          }
          this.$message({
            type: 'success',
            message: '删除成功!'
          });
        }).catch(error => {
          this.$message({
            type: 'error',
            message: error.response.data.detail
          });
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    },
    AddDepartmentForm (formName) {
      let that = this
      that.$refs[formName].validate((valid) => {
        if (valid) {
          let approver_chain = []
          let Data = {
            "name": this.form.name,
            "detail": this.form.detail,
            "email": this.form.email,
            "permissions": this.form.permission,
            "desc": this.form.desc,
          }
          AddDepartment(Data).then(response => {
            if (response.status === 201) {
              that.centerDialogVisible = false
              this.$message.success('添加成功')
              setTimeout(() => {
                this.fetchData()
              }, 2000)
            } else {
              console.log(response)
            }
          }).catch(error => {
            console.log(error)
          })
        } else {
          console.log('error')
        }
      })
    },
    resetForm (formName) {
      this.$refs[formName].resetFields();
      this.centerDialogVisible = false
    },
    handleSizeChange: function (pageSize) {
      this.pageSize = pageSize
      this.findPage(this.currentPage, this.pageSize);
    },
    handleCurrentChange: function (currentPage) {
      this.currentPage = currentPage
      this.findPage(this.currentPage, this.pageSize)
    },
    findPage (pageCode, pageSize) {
      getDepartments({ page: pageCode, page_size: pageSize }).then(response => {
        this.list = response.data.results
        this.total = response.data.count
      }).catch(error => {
        console.log(error)
      })
    },
    checkDesc (value) {
      if (value) {
        return value
      }
      return '-'
    },
    handleEdit (index, row) {
      this.editformData = Object.assign({}, row)
      this.$set(this.editformData, 'permission', [])
      for (let i = 0; i < row.permissions_set.length; i++) {
        this.editformData.permission.push(row.permissions_set[i].id)
      }
      this.editType = 'update'
      this.diaIsShow = true
      this.$nextTick(() => {
        this.$refs.diaForm.clearValidate()
      })
      this.rowIndex = index
    },
    changeTab (form, type) {
      this.$refs[form].validate(valid => {
        if (valid) {
          if (type === 'update') {

            let post_data = {
              "name": this.editformData.name,
              "detail": this.editformData.detail,
              "email": this.editformData.email,
              "permissions": this.editformData.permission,
              "desc": this.editformData.desc,
            }
            EditDepartment(this.editformData.id, post_data).then(response => {
              let start = (this.currentPage - 1) * this.pageSize
              this.list[start + this.rowIndex] = Object.assign(
                {},
                this.editformData
              )
              // 解决数组不能通过索引响应数据变化
              this.$set(
                this.list,
                this.rowIndex,
                Object.assign({}, this.editformData)
              )
              this.$message({
                title: '成功',
                message: '修改成功',
                type: 'success'
              })
              this.diaIsShow = false
              this.fetchData()
            }).catch(error => {
              this.$message({
                title: '失败',
                message: error.response.data,
                type: 'error'
              })
              return
            })
          }
        } else {
          return
        }
      })
    }
  }
}
</script>
<style>
/* .dialogbody {
  margin-left: 15%;
} */

/* .dialog-form {
  margin-left: 70px;
} */
.el-upload-dragger {
  height: 110px;
}
.el-upload-dragger .el-icon-upload {
  margin: 10px 0 10px 0;
}
.el-upload-list {
  margin: 0 80px 0 0;
}
.config_element {
  margin-top: 20px;
}
</style>
