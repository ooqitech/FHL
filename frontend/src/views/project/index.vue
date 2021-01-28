<template>
  <div class="app-container">

    <el-drawer title="添加应用"
               :visible.sync="drawer"
               :direction="direction"
               destroy-on-close
               :close-on-press-escape=false
               @close="resetForm('form')">
      <div class="dialog-form">
        <el-form ref="form"
                 :model="form"
                 :rules="dialogRules"
                 label-width="100px"
                 class="dialogbody">
          <el-form-item label="应用类型"
                        prop="project_type">
            <el-radio-group v-model="form.project_type">
              <el-radio label="1">JAVA</el-radio>
              <el-radio label="2">Jar</el-radio>
              <el-radio label="3">H5</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="应用名称"
                        prop="app_name">
            <el-input v-model="form.app_name"
                      style="width: 81%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item label="中文名称"
                        prop="chinese_name">
            <el-input v-model="form.chinese_name"
                      style="width: 81%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item class="config_element"
                        label="所属部门"
                        prop="depart_group">
            <el-select v-model="form.depart_group"
                       filterable
                       placeholder="请选择"
                       style="width: 81%">
              <el-option v-for="item in departments"
                         :key="item.id"
                         :label="item.name"
                         :value="item.id"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item class="config_element"
                        label="开发部门"
                        prop="dev_group">
            <el-select v-model="form.dev_group"
                       filterable
                       placeholder="请选择"
                       style="width: 81%">
              <el-option v-for="item in departments"
                         :key="item.id"
                         :label="item.name"
                         :value="item.id"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item class="config_element"
                        label="测试部门"
                        prop="test_group">
            <el-select v-model="form.test_group"
                       filterable
                       placeholder="请选择"
                       style="width: 81%">
              <el-option v-for="item in departments"
                         :key="item.id"
                         :label="item.name"
                         :value="item.id"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item v-if="form.project_type === '3'"
                        label="发布路径"
                        prop="path">
            <el-input v-model="form.path"
                      style="width: 81%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item v-if="form.project_type === '1'"
                        label="ROOT.war"
                        prop="is_root">
            <el-radio-group v-model="form.is_root">
              <el-radio label="true">是</el-radio>
              <el-radio label="false">否</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="备注"
                        prop="detail">
            <el-input v-model="form.detail"
                      style="width: 81%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item class="drawer-form">
            <el-button @click="resetForm('form')">取 消</el-button>
            <el-button type="primary"
                       @click="AddProject('form')">确 定</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-drawer>

    <el-drawer title="编辑应用"
               :visible.sync="edrawer"
               :direction="direction"
               destroy-on-close
               :close-on-press-escape=false
               @close="reseteditForm('editform')">
      <div class="dialog-form">
        <el-form ref="editform"
                 :model="form"
                 :rules="dialogRules"
                 label-width="100px"
                 class="dialogbody">
          <el-form-item label="应用类型"
                        prop="project_type">
            <el-radio-group v-model="form.project_type">
              <el-radio :label="form.project_type"
                        v-if="form.project_type === 1">JAVA</el-radio>
              <el-radio :label="form.project_type"
                        v-if="form.project_type === 2">Jar</el-radio>
              <el-radio :label="form.project_type"
                        v-if="form.project_type === 3">H5</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="应用名称"
                        prop="app_name">
            <el-input v-model="form.app_name"
                      style="width: 81%"
                      disabled></el-input>
          </el-form-item>
          <el-form-item label="中文名称"
                        prop="chinese_name">
            <el-input v-model="form.chinese_name"
                      style="width: 81%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item class="config_element"
                        label="所属部门"
                        prop="depart_group">
            <el-select v-model="form.depart_group"
                       filterable
                       placeholder="请选择"
                       style="width: 81%">
              <el-option v-for="item in departments"
                         :key="item.id"
                         :label="item.name"
                         :value="item.id"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item class="config_element"
                        label="开发部门"
                        prop="dev_group">
            <el-select v-model="form.dev_group"
                       filterable
                       placeholder="请选择"
                       style="width: 81%">
              <el-option v-for="item in departments"
                         :key="item.id"
                         :label="item.name"
                         :value="item.id"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item class="config_element"
                        label="测试部门"
                        prop="test_group">
            <el-select v-model="form.test_group"
                       filterable
                       placeholder="请选择"
                       style="width: 81%">
              <el-option v-for="item in departments"
                         :key="item.id"
                         :label="item.name"
                         :value="item.id"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item v-if="form.project_type === 3"
                        label="发布路径"
                        prop="path">
            <el-input v-model="form.path"
                      style="width: 81%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item v-if="form.project_type === 1"
                        label="ROOT.war"
                        prop="is_root">
            <el-radio-group v-model="form.is_root">
              <el-radio :label="form.is_root"
                        v-if="form.is_root">是</el-radio>
              <el-radio :label="form.is_root"
                        v-else>否</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="备注"
                        prop="detail">
            <el-input v-model="form.detail"
                      style="width: 81%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item class="drawer-form">
            <el-button @click="reseteditForm('editform')">取 消</el-button>
            <el-button type="primary"
                       @click="changeTab('editform', editType)">确 定</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-drawer>

    <el-form :inline="true"
             :model="formInline"
             class="demo-form-inline">
      <el-form-item label="">
        <el-input v-model="formInline.app_name"
                  placeholder="项目名称" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary"
                   @click="onSearch">搜索</el-button>
      </el-form-item>
      <el-form-item>
        <el-button type="primary"
                   @click="handleAdd">添加应用</el-button>
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
      <el-table-column label="项目名称"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column label="项目中文名"
                       align="center">
        <template slot-scope="scope">
          <span v-if="scope.row.chinese_name">{{ scope.row.chinese_name }}</span>
          <span v-else>{{ scope.row.app_cname }}</span>
        </template>
      </el-table-column>
      <el-table-column label="部门"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.department }}
        </template>
      </el-table-column>
      <el-table-column label="开发部门"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.dev }}
        </template>
      </el-table-column>
      <el-table-column label="项目类型"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.app_type }}
        </template>
      </el-table-column>
      <el-table-column label="状态"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.app_status }}
        </template>
      </el-table-column>
      <el-table-column label="创建时间"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.create_time }}
        </template>
      </el-table-column>
      <el-table-column label="更新时间"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.update_time }}
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
import { getProjects, AddProjects, editProjects, getProjectById, deleteProject, getSreBusiness, getEmployee } from '@/api/projects'
import { getDepartments } from '@/api/account'
import { setTimeout } from 'timers';
export default {
  data () {
    var checkPath = (rule, value, callback) => {
      if (this.form.project_type === '3') {
        if (!value) {
          return callback(new Error(`发布路径不能为空`));
        }
      }
      callback();
    };
    var checkIsRoot = (rule, value, callback) => {
      if (this.form.project_type === '1') {
        if (!value) {
          return callback(new Error(`请选择war包是否为ROOT`));
        }
      }
      callback();
    };
    return {
      list: null,
      listLoading: true,
      formInline: {
        app_name: ''
      },
      fileList: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      allApps: '',
      appObject: {},
      drawer: false,
      edrawer: false,
      direction: 'rtl',
      dialogRules: {
        project_type: [{ required: true, trigger: 'blur', message: '应用类型未选择' }],
        app_name: [{ required: true, trigger: 'blur', message: '应用名称不能为空' }],
        chinese_name: [{ required: true, message: '中文名称不能为空', trigger: 'blur' }],
        depart_group: [{ required: true, trigger: 'blur', message: '所属部门不能为空' }],
        dev_group: [{ required: true, trigger: 'blur', message: '开发部门不能为空' }],
        test_group: [{ required: true, trigger: 'blur', message: '测试部门不能为空' }],
        path: [{ required: true, trigger: 'blur', validator: checkPath }],
        is_root: [{ required: true, trigger: 'blur', validator: checkIsRoot }],
        detail: [{ required: true, trigger: 'blur', message: '备注不能为空' }],
      },
      form: {
        project_type: '',
        app_name: '',
        chinese_name: '',
        depart_group: '',
        dev_group: '',
        test_group: '',
        path: '',
        is_root: '',
        detail: '',
      },
      // editform: {
      //   project_type: '',
      //   app_name: '',
      //   chinese_name: '',
      //   cat_name: '',
      //   elk_name: '',
      //   business: '',
      //   role_a: '',
      //   role_b: '',
      //   depart_group: '',
      //   dev_group: '',
      //   test_group: '',
      //   path: '',
      //   is_root: '',
      //   detail: '',
      // },
      editType: '',
      departments: [],
      departObj: {},
      formId: ''
    }
  },
  created () {
    this.fetchData()
    this.getGroup()
  },
  methods: {
    fetchData () {
      this.listLoading = true
      getProjects({ per_page: this.pageSize, page: this.currentPage }).then(response => {
        this.list = response.data.results
        this.total = response.data.count
        this.listLoading = false
      }).catch(error => {
        console.log(error)
      })
    },
    getGroup () {
      getDepartments({ page_size: 100 }).then(response => {
        let results = response.data.results
        for (let i = 0; i < results.length; i++) {
          this.departments.push({
            id: results[i].id,
            name: results[i].name
          })
          this.departObj[results[i].name] = results[i].id
        }
        console.log(this.departments)
      }).catch(error => {
        console.log(error)
      })
    },
    onSearch () {
      // let data = {}
      // if (this.formInline.app_name) {
      //   data = { app_name: this.formInline.app_name }
      // } else {
      //   data = { per_page: this.pageSize, page: this.currentPage }
      // }
      getProjects({ app_name: this.formInline.app_name }).then(response => {
        this.list = response.data.results
        this.total = response.data.count
      }).catch(error => {
        console.log(error)
      })
    },
    handleSizeChange: function (pageSize) { // 每页条数切换
      this.pageSize = pageSize
      this.findPage(this.currentPage, this.pageSize)
    },
    handleCurrentChange: function (currentPage) {//页码切换
      this.currentPage = currentPage
      this.findPage(currentPage, this.pageSize)
    },
    findPage (pageCode, pageSize) {
      getProjects({ app_name: this.formInline.app_name, page: pageCode, per_page: pageSize }).then(response => {
        this.list = response.data.results
        this.total = response.data.count
      }).catch(error => {
        console.log(error)
      })
    },
    handleAdd () {
      this.drawer = true
      Object.keys(this.form).forEach(key => this.form[key] = '');
    },
    resetForm (formName) {
      this.drawer = false
      this.$refs[formName].resetFields();
    },
    reseteditForm (formName) {
      this.edrawer = false
      // this.editform = {}
      this.$refs[formName].resetFields();
    },
    AddProject (formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          let Data = {
            "project_type": this.form.project_type,
            "name": this.form.app_name,
            "chinese_name": this.form.chinese_name,
            "department_id": this.form.depart_group,
            "dev_group_id": this.form.dev_group,
            "test_group_id": this.form.test_group,
            "is_root": this.checkValue(this.form.is_root),
            "app_dir": this.form.path,
            "detail": this.form.detail
          }
          console.log(Data)
          AddProjects(Data).then(response => {
            this.drawer = false
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
    checkValue (value) {
      if (value === "true") {
        return true
      }
      return false
    },
    handleDelete (index, row) {
      this.$confirm('你真的要删除 ' + row.name + ' 么？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteProject(row.id).then(response => {
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
    handleEdit (index, row) {

      Object.keys(this.form).forEach(key => this.form[key] = '');
      getProjectById(row.id).then(response => {

        let result = response.data
        this.formId = row.id
        this.form.app_name = result.name
        this.form.project_type = result.project_type
        this.form.chinese_name = result.chinese_name
        this.form.depart_group = this.departObj[result.department]
        this.form.dev_group = this.departObj[result.dev]
        this.form.test_group = this.departObj[result.test]
        this.form.detail = result.detail
        this.form.is_root = false
        if (result.project_type === 1 || result.project_type === 2) {
          this.form.is_root = result.is_root
        } else {
          this.form.path = result.app_dir
        }
      }).catch(error => {
        console.log(error)
      })

      console.log(this.form)
      this.editType = 'update'
      this.edrawer = true
      this.$nextTick(() => {
        this.$refs.editform.clearValidate()
      })
      this.rowIndex = index
    },
    changeTab (form, type) {
      this.$refs[form].validate(valid => {
        if (valid) {
          if (type === 'update') {

            let Data = {
              "project_type": this.form.project_type,
              "chinese_name": this.form.chinese_name,
              "department_id": this.form.depart_group,
              "dev_group_id": this.form.dev_group,
              "test_group_id": this.form.test_group,
              "is_root": this.form.is_root,
              "app_dir": this.form.path,
              "detail": this.form.detail
            }
            console.log(Data)
            editProjects(this.formId, Data).then(response => {
              setTimeout(() => {
                this.fetchData()
              }, 1000)
              this.$message({
                title: '成功',
                message: '修改成功',
                type: 'success'
              })
              this.edrawer = false
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
<style scoped>
.pagination {
  margin: 20px 0;
  text-align: right;
}
.el-drawer {
  margin-top: 50px;
}
.drawer-form {
  text-align: center;
}
.el-drawer__container >>> .el-drawer {
  width: 500px;
}
</style>
