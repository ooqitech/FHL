<template>
  <div class="app-container">
    <el-alert title="ECS资源同步阿里云，页面中仅展示已绑定应用的ECS主机信息; 请在绑定资源界面中关联您的资源与应用"
              type="info"
              effect="light"
              :closable="false">
    </el-alert>
    <el-dialog title="应用绑定ECS"
               :visible.sync="bindDialogVisible"
               width="40%"
               destroy-on-close
               :close-on-click-modal=false
               :close-on-press-escape=false
               @close="resetForm('bindForm')">
      <div class="dialog-form">
        <el-form ref="bindForm"
                 :model="bindEcsForm"
                 :rules="bindecsRules"
                 label-width="100px">
          <el-form-item label="应用名"
                        prop="app_name">
            <el-select v-model="bindEcsForm.app_name"
                       filterable
                       placeholder="请选择"
                       style="width: 84%">
              <el-option v-for="item in allApps"
                         :key="item.id"
                         :label="item.name"
                         :value="item.id"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="关联实例"
                        prop="instance">
            <el-transfer filterable
                         :titles="['可用实例', '已选实例']"
                         filter-placeholder="请输入搜索内容"
                         v-model="bindEcsForm.instance"
                         :data="instanceData">
            </el-transfer>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer"
            class="dialog-footer">
        <el-button @click="resetForm('bindForm')">取 消</el-button>
        <el-button type="primary"
                   @click="bindEcs('bindForm')">确 定</el-button>
      </span>
    </el-dialog>

    <el-form :inline="true"
             :model="formSearch"
             class="demo-form-inline">
      <el-form-item label="">
        <el-input v-model="formSearch.app_name"
                  placeholder="应用名" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary"
                   @click="handleSearch">搜索</el-button>
      </el-form-item>
      <el-form-item>
        <el-button type="primary"
                   @click="handleDownload">模板下载</el-button>
      </el-form-item>
      <el-form-item>
        <div>

          <el-upload class="upload-demo"
                     :http-request="handleFile"
                     :multiple="false"
                     :limit="1"
                     action="sss"
                     clearFiles
                     :on-exceed="handleExceed"
                     :file-list="fileList"
                     :show-file-list="false"
                     :before-upload="beforeAvatarUpload">
            <el-tooltip class="item"
                        effect="dark"
                        content="您需要下载模板并填入信息后再上传"
                        placement="top">

              <el-button type="primary">批量资源绑定</el-button>
            </el-tooltip>
          </el-upload>
        </div>
      </el-form-item>
      <el-form-item>
        <el-button :loading="loading"
                   type="primary"
                   @click="handleBind">绑定资源</el-button>
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
          {{ scope.row.app_id }}
        </template>
      </el-table-column>
      <el-table-column label="应用名称"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.app_name }}
        </template>
      </el-table-column>
      <el-table-column label="主机名"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.hostname }}
        </template>
      </el-table-column>
      <el-table-column label="内网IP"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.inner_ip_addr }}
        </template>
      </el-table-column>
      <el-table-column label="外网IP"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.outer_ip_addr }}
        </template>
      </el-table-column>
      <el-table-column label="弹性IP"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.elastic_ip }}
        </template>
      </el-table-column>
      <el-table-column label="vCPU"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.cpu_count }}
        </template>
      </el-table-column>
      <el-table-column label="MEM"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.memory_size }}
        </template>
      </el-table-column>
      <el-table-column label="DISK"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.disk_size }}
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
                       width="120">
        <template slot-scope="scope">
          <el-button size="mini"
                     type="danger"
                     icon="el-icon-s-operation"
                     round
                     @click="unBind(scope.$index, scope.row)">解绑资源</el-button>
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
import { getCmdb, getEcs, getTemplate, unBindEcs, getEcsIdle, appbindEcs, bindsEcs } from '@/api/cmdb'
import { getAllProject } from '@/api/projects'
import { setTimeout } from 'timers';
export default {
  data () {
    return {
      list: null,
      listLoading: true,
      loading: false,
      dialogList: null,
      dialogLoading: true,
      formSearch: {
        app_name: ''
      },
      bindEcsForm: {
        app_name: '',
        instance: []
      },
      bindecsRules: {
        app_name: [{ required: true, trigger: 'blur', message: '应用名不能为空' }],
        instance: [{ required: true, trigger: 'blur', message: 'ECS未选择' }]
      },
      centerDialogVisible: false,
      bindDialogVisible: false,
      instanceData: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      instances: {},
      allApps: [],
      fileList: []
    }
  },
  created () {
    this.fetchData()
    this.getAllProjects()
  },
  methods: {
    fetchData () {
      this.listLoading = true
      getCmdb().then(response => {
        this.list = response.data.results
        this.total = response.data.count
        this.listLoading = false
      }).catch(error => {
        this.listLoading = false
        console.log(error)
      })
    },
    getAllProjects () {
      getAllProject().then(response => {
        let projects = response.data
        for (let i = 0; i < projects.length; i++) {
          if (projects[i].name.split('-')[0] !== "h5") {
            this.allApps.push({
              id: projects[i].id,
              name: projects[i].name
            })
          }
        }
      }).catch(error => {
        console.log(error.response)
      })
    },
    handleSearch () {
      getCmdb({
        app_name: this.formSearch.app_name
      }).then(response => {
        this.list = response.data.results
        this.total = response.data.count
      }).catch(error => {
        console.log(error)
      })
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
      getCmdb({ page: pageCode, page_size: pageSize }).then(response => {
        this.list = response.data.results
        this.total = response.data.count
      }).catch(error => {
        console.log(error)
      })
    },
    unBind (index, row) {
      this.$confirm('你真的要解绑定 ' + row.hostname + ' 么？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        unBindEcs(row.id).then(response => {
          for (var i = 0; i < this.list.length; i++) {
            if (this.list[i].id === row.id) {
              this.list.splice(i, 1)
            }
          }
          this.total -= 1
          this.$message({
            type: 'success',
            message: '解绑定成功!'
          });
        }).catch(() => {
          this.$message({
            type: 'error',
            message: '解绑定失败!'
          });
        })
      }).catch(() => { })
    },
    handleDownload () {
      getTemplate().then(response => {
        let blob = new Blob([response.data], { type: "application/vnd.ms-excel" });
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob);
        link.download = 'ecs_template.csv'
        link.click()
        console.log('download success')
      }).catch(error => {
        console.log(error)
      })
    },
    handleBind () {
      this.loading = true
      this.instanceData = []
      getEcsIdle().then(response => {
        let results = response.data
        for (let i = 0; i < results.length; i++) {
          this.instanceData.push({
            key: results[i].id,
            label: results[i].inner_ip_addr
          })
        }
      }).catch(error => {
        console.log(error)
      })
      setTimeout(() => {
        this.loading = false
        this.bindDialogVisible = true
      }, 1000)
    },
    bindEcs (formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          let data = {
            app_id: this.bindEcsForm.app_name,
            ecs_list: this.bindEcsForm.instance
          }
          appbindEcs(data).then(response => {
            if (response.status === 200) {
              this.bindDialogVisible = false
              this.$message.success('绑定成功')
              setTimeout(() => {
                this.fetchData()
              }, 2000)
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
      this.bindDialogVisible = false
      this.$refs[formName].resetFields();
    },
    beforeAvatarUpload (file) {
      const isSQL = file.name.split('.')[file.name.split('.').length - 1] === 'csv';
      const isLt2M = file.size / 1024 / 1024 < 5;

      if (!isSQL) {
        this.$message.error('上传文件只能是 csv 格式!');
      }

      if (!isLt2M) {
        this.$message.error('上传文件大小不能超过 5MB!');
      }
      return isSQL && isLt2M
    },
    handleFile (fileobj) {
      this.fileList.push(fileobj.file)
      let formData = new FormData()
      formData.append('file', this.fileList[0])
      bindsEcs(formData).then(response => {
        this.$message.success('批量绑定成功')
        this.fileList = []
        setTimeout(() => {
          this.fetchData()
        }, 2000)
      }).catch(error => {
        this.fileList = []
        console.log(error)
      })
    },
    handleExceed (files, fileList) {
      this.$message.warning(`最多上传 ${files.length} 个文件`)
    },
  }
}
</script>
<style scoped>
.config_element {
  margin-top: 20px;
}
.pagination {
  margin: 20px 0;
  text-align: right;
}

div >>> .el-form-item__content {
  line-height: 0;
}
</style>
<style>
.el-alert {
  margin: 0 0 15px 0;
}
</style>
