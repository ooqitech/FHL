<template>
  <div class="app-container">
    <el-dialog title="添加用户"
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
          <el-form-item label="用户名"
                        prop="username">
            <el-input v-model="form.username"
                      style="width: 71%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item label="密码"
                        prop="password">
            <el-input type="password"
                      v-model="form.password"
                      style="width: 71%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item label="邮箱"
                        prop="email">
            <el-input v-model="form.email"
                      style="width: 71%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item label="电话"
                        prop="phone">
            <el-input v-model="form.phone"
                      style="width: 71%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item label="部门"
                        prop="department">
            <el-select v-model="form.department"
                       filterable
                       placeholder="请选择"
                       style="width: 71%">
              <el-option v-for="item in allDept"
                         :key="item.id"
                         :label="item.name"
                         :value="item.id"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="用户组">
            <el-select v-model="form.group"
                       filterable
                       placeholder="请选择"
                       style="width: 71%">
              <el-option v-for="item in allGroup"
                         :key="item.id"
                         :label="item.name"
                         :value="item.id"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="管理员"
                        prop="is_superuser">
            <el-checkbox-group v-model="form.is_superuser">
              <el-checkbox label="是"
                           name="is_superuser"></el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer"
            class="dialog-footer">
        <el-button @click="resetForm('form')">取 消</el-button>
        <el-button type="primary"
                   @click="AddUserForm('form')">确 定</el-button>
      </span>
    </el-dialog>

    <el-form :inline="true"
             class="demo-form-inline">
      <el-form-item>
        <el-button type="primary"
                   @click="centerDialogVisible = true">添加用户</el-button>
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
      <el-table-column label="用户名"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.username }}
        </template>
      </el-table-column>
      <el-table-column label="邮箱"
                       align="center">
        <template slot-scope="scope">
          {{ formatValue(scope.row.email) }}
        </template>
      </el-table-column>
      <el-table-column label="手机"
                       align="center">
        <template slot-scope="scope">
          {{ formatValue(scope.row.phone) }}
        </template>
      </el-table-column>
      <el-table-column label="所属部门"
                       align="center">
        <template slot-scope="scope">
          {{ formatDept(scope.row.department) }}
        </template>
      </el-table-column>
      <el-table-column label="所属组"
                       align="center">
        <template slot-scope="scope">
          {{ formatGroup(scope.row.group) }}
        </template>
      </el-table-column>
      <el-table-column label="状态"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.is_active }}
        </template>
      </el-table-column>
      <el-table-column label="是否管理员"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.is_superuser }}
        </template>
      </el-table-column>
      <el-table-column label="创建时间"
                       align="center">
        <template slot-scope="scope">
          {{ formatDate(scope.row.date_joined) }}
        </template>
      </el-table-column>
      <el-table-column label="最后登录时间"
                       align="center">
        <template slot-scope="scope">
          {{ formatDate(scope.row.last_login) }}
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
          <el-button v-if="scope.row.username === 'admin'"
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
                   @size-change="handleSizeChange1"
                   @current-change="handleCurrentChange1"
                   :current-page="currentPage1"
                   :page-sizes="[10, 20, 50, 100]"
                   :page-size="pageSize"
                   layout="total, sizes, prev, pager, next, jumper"
                   :total="total" />
    <el-dialog title="用户编辑"
               :visible.sync="diaIsShow"
               class="diaForm"
               width="30%">
      <el-form ref="diaForm"
               :model="editformData"
               :rules="Rules"
               label-width="100px">
        <el-form-item label="用户名"
                      prop="username">
          <el-input type="text"
                    v-model="editformData.username"
                    style="width: 71%"
                    disabled></el-input>
        </el-form-item>
        <el-form-item label="邮箱"
                      prop="email">
          <el-input v-model="editformData.email"
                    style="width: 71%"
                    autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="电话"
                      prop="phone">
          <el-input v-model="editformData.phone"
                    style="width: 71%"
                    autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="部门"
                      prop="department">
          <el-select v-model="editformData.department"
                     filterable
                     placeholder="请选择"
                     style="width: 71%">
            <el-option v-for="item in allDept"
                       :key="item.id"
                       :label="item.name"
                       :value="item.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="用户组">
          <el-select v-model="editformData.group"
                     filterable
                     placeholder="请选择"
                     style="width: 71%">
            <el-option v-for="item in allGroup"
                       :key="item.id"
                       :label="item.name"
                       :value="item.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="管理员"
                      prop="is_superuser">
          <el-checkbox-group v-model="editformData.is_superuser">
            <el-checkbox label="是"
                         name="is_superuser"></el-checkbox>
          </el-checkbox-group>
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
import { getUsers, getDepartments, getGroups, AddUser, DeleteUser, EditUser } from '@/api/account.js'
import { setTimeout } from 'timers';
export default {
  data () {
    var checkPhone = (rule, value, callback) => {
      if (!value) {
        return callback(new Error('手机号不能为空'));
      } else {
        const reg = /^1[3|4|5|7|8][0-9]\d{8}$/
        console.log(reg.test(value));
        if (reg.test(value)) {
          callback();
        } else {
          return callback(new Error('请输入正确的手机号'));
        }
      }
    };
    return {
      multiValue: [],
      list: null,
      listLoading: true,
      diaIsShow: false,
      editformData: {},
      editType: '',
      dialogRules: {
        username: [{ required: true, trigger: 'blur', message: '用户名不能为空' }],
        password: [{ required: true, trigger: 'blur', message: '密码不能为空' }, { min: 6, message: '密码不少于6位', trigger: 'blur' }],
        email: [{ required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }],
        phone: [{ required: true, validator: checkPhone, trigger: 'blur' }],
        department: [{ required: true, trigger: 'blur', message: '部门不能为空' }],
      },
      Rules: {
        username: [{ required: true, trigger: 'blur', message: '用户名不能为空' }],
        email: [{ required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }],
        phone: [{ required: true, validator: checkPhone, trigger: 'blur' }],
        department: [{ required: true, trigger: 'blur', message: '部门不能为空' }],
      },
      form: {
        username: '',
        password: '',
        email: '',
        phone: '',
        department: '',
        group: '',
        is_superuser: false
      },
      pickerOptions: {
        disabledDate (time) {
          return time.getTime() > Date.now()
        }
      },
      // value: true,
      centerDialogVisible: false,
      total: 0,
      currentPage1: 1,
      pageSize: 10,
      allDept: [],
      allGroup: [],
      groupObj: {},
      deptObj: {},
      rowIndex: 0
      ,
    }
  },
  created () {
    this.fetchData()
    this.getDepart()
    this.fetchGroup()
  },
  methods: {
    fetchData () {
      this.listLoading = true
      getUsers().then(response => {
        this.list = response.data.results
        this.total = response.data.count
        this.listLoading = false
      }).then(error => {
        console.log(error)
      })
    },
    getDepart () {
      getDepartments().then(response => {
        let results = response.data.results
        for (let i in results) {
          this.allDept.push({
            id: results[i].id,
            name: results[i].name
          })
          this.deptObj[results[i].id] = results[i].name
        }
      }).then(error => {
        console.log(error)
      })
    },
    fetchGroup () {
      getGroups().then(response => {
        let results = response.data.results
        for (let i in results) {
          this.allGroup.push({
            id: results[i].id,
            name: results[i].name
          })
          this.groupObj[results[i].id] = results[i].name
        }
      }).then(error => {
        console.log(error)
      })
    },
    formatDate (date) {
      if (date) {
        date = new Date(date)
        return (
          date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate() + ' ' + date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds()
        )
      }
      return '-'
    },
    formatValue (value) {
      if (value) {
        return value
      }
      return '-'
    },
    formatDept (value) {
      if (value) {
        return this.deptObj[value]
      }
      return '-'
    },
    formatGroup (value) {
      if (value) {
        return this.groupObj[value]
      }
      return '-'
    },
    handleDelete (index, row) {
      this.$confirm('你真的要删除 ' + row.username + ' 么？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        DeleteUser(row.id).then(response => {
          for (var i = 0; i < this.list.length; i++) {
            if (this.list[i].id === row.id) {
              this.list.splice(i, 1)
            }
          }
          this.$message({
            type: 'success',
            message: '删除成功!'
          });
        }).catch(() => {
          this.$message({
            type: 'error',
            message: '删除失败!'
          });
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    },
    AddUserForm (formName) {
      let that = this
      that.$refs[formName].validate((valid) => {
        if (valid) {
          let Data = {
            "username": this.form.username,
            "password": this.form.password,
            "email": this.form.email,
            "phone": this.form.phone,
            "department": this.form.department,
            "group": this.form.group,
            "is_superuser": this.form.is_superuser,
            "is_active": true
          }
          AddUser(Data).then(response => {
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
      this.form.group = ''
      this.centerDialogVisible = false
    },
    handleSizeChange1: function (pageSize) { // 每页条数切换
      this.pageSize = pageSize
      this.findPage(this.currentPage1, this.pageSize);
    },
    handleCurrentChange1: function (currentPage) { // 页码切换
      this.currentPage1 = currentPage
      this.findPage(this.currentPage1, this.pageSize)
    },
    findPage (pageCode, pageSize) {
      getUsers({ page: pageCode, page_size: pageSize }).then(response => {
        this.list = response.data.results
        this.total = response.data.count
      }).catch(error => {
        console.log(error)
      })
    },
    handleEdit (index, row) {
      this.editformData = Object.assign({}, row)
      console.log(this.editformData)
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
              "username": this.editformData.username,
              "email": this.editformData.email,
              "phone": this.editformData.phone,
              "department": this.editformData.department,
              "group": this.editformData.group,
              "is_superuser": this.editformData.is_superuser,
            }
            EditUser(this.editformData.id, post_data).then(response => {
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
              this.editformData.group_name = ''
              this.diaIsShow = false
            }).catch(error => {
              console.log(error)
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
  margin-left: 60px;
} */
.config_element {
  margin-top: 20px;
}
.pagination {
  margin: 20px 0;
  text-align: right;
}
</style>
