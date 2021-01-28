<template>
  <div class="app-container">
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
          {{ scope.row.department_name }}
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
                       width="150">
        <template slot-scope="scope">
          <el-button size="mini"
                     type="primary"
                     icon="el-icon-edit"
                     round
                     @click="handleEdit(scope.$index, scope.row)">修改密码</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination">
      <el-pagination v-if="total > 0"
                     @size-change="handleSizeChange"
                     @current-change="handleCurrentChange"
                     :current-page="currentPage"
                     :page-sizes="[10, 20, 50, 100]"
                     :page-size="pageSize"
                     layout="total, sizes, prev, pager, next, jumper"
                     :total="total" />
    </div>
    <el-dialog title="修改密码"
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
        <el-form-item label="密码"
                      prop="password">
          <el-input type="password"
                    v-model="editformData.password"
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
import { getUsers, SetUserPassword } from '@/api/account.js'
import { constants } from 'fs';
import { setTimeout } from 'timers';
import { mapGetters } from 'vuex'
export default {
  filters: {
    statusFilter (status) {
      const statusMap = {
        published: 'success',
        draft: 'gray',
        deleted: 'danger'
      }
      return statusMap[status]
    }
  },
  data () {
    return {
      list: null,
      listLoading: true,
      diaIsShow: false,
      editformData: {},
      editType: '',
      Rules: {
        username: [{ required: true, trigger: 'blur', message: '用户名不能为空' }],
        password: [{ required: true, trigger: 'blur', message: '密码不能为空' }, { min: 6, message: '密码不少于6位', trigger: 'blur' }],
      },
      form: {
        username: '',
        password: '',
        email: '',
        phone: '',
        department: '',
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
      currentPage: 1,
      pageSize: 10,
      allDept: [],
      deptObj: {},
      rowIndex: 0,
      currUser: '',
      is_superuser: false
    }
  },
  created () {

    console.log('name', name)
    this.currUser = name
    this.fetchData()
  },
  methods: {
    fetchData () {
      this.listLoading = true
      getUsers().then(response => {
        this.list = response.data.results
        this.total = response.data.count
        this.listLoading = false
      }).catch(error => {
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
      getUsers({ page: pageCode, page_size: pageSize }).then(response => {
        this.list = response.data.results
        this.total = response.data.count
      }).catch(error => {
        console.log(error)
      })
    },
    handleEdit (index, row) {
      this.editformData = Object.assign({}, row)
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
              "password": this.editformData.password,
            }
            SetUserPassword(this.editformData.id, post_data).then(response => {
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
  },
  computed: {
    ...mapGetters([
      'name'
    ])
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
.pagination {
  margin: 20px 0;
  text-align: right;
}
</style>
