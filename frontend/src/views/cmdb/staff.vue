<template>
  <div class="app-container">
    <el-dialog title="添加人员"
               :visible.sync="centerDialogVisible"
               width="30%"
               center
               destroy-on-close
               :close-on-click-modal=false
               :close-on-press-escape=false
               @close="resetForm('form')">
      <div class="dialog-form">
        <el-form ref="form"
                 :model="form"
                 :rules="dialogRules"
                 label-width="100px"
                 class="dialogbody">
          <el-form-item label="中文名"
                        prop="name">
            <el-input v-model="form.name"
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
        </el-form>
      </div>
      <span slot="footer"
            class="dialog-footer">
        <el-button @click="resetForm('form')">取 消</el-button>
        <el-button type="primary"
                   @click="handleAddStaff('form')">确 定</el-button>
      </span>
    </el-dialog>

    <el-form :inline="true"
             class="demo-form-inline">
      <el-form-item>
        <el-button type="primary"
                   @click="centerDialogVisible = true">添加人员</el-button>
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
      <el-table-column label="姓名"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column label="手机"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.phone }}
        </template>
      </el-table-column>
      <el-table-column label="邮箱"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.email }}
        </template>
      </el-table-column>
      <el-table-column align="center"
                       prop="created_at"
                       label="操作"
                       width="200">
        <template slot-scope="scope">
          <el-button size="mini"
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

  </div>
</template>

<script>
import { getStaff, AddStaff, DeleteStaff } from '@/api/cmdb'
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
      list: null,
      listLoading: true,
      dialogRules: {
        name: [{ required: true, trigger: 'blur', message: '中文名不能为空' }],
        email: [{ required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }],
        phone: [{ required: true, validator: checkPhone, trigger: 'blur' }]
      },
      form: {

        name: '',
        email: '',
        phone: ''
      },
      centerDialogVisible: false,
      total: 0,
      currentPage: 1,
      pageSize: 10,
      rowIndex: 0,
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      getStaff().then(response => {
        this.list = response.data.results
        this.total = response.data.count
        this.listLoading = false
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
        DeleteStaff(row.id).then(response => {
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
          console.log(error)
        })
      }).catch(() => { })
    },
    handleAddStaff (formName) {
      let that = this
      that.$refs[formName].validate((valid) => {
        if (valid) {
          let Data = {
            "name": this.form.name,
            "email": this.form.email,
            "phone": this.form.phone,
          }
          AddStaff(Data).then(response => {
            that.centerDialogVisible = false
            this.$message.success('添加成功')
            setTimeout(() => {
              this.fetchData()
            }, 2000)
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
      getStaff({ page: pageCode, page_size: pageSize }).then(response => {
        this.list = response.data.results
        this.total = response.data.count
      }).catch(error => {
        console.log(error)
      })
    }
  }
}
</script>
<style>
.pagination {
  margin: 20px 0;
  text-align: right;
}
</style>
