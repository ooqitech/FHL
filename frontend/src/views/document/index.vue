<template>
  <div class="app-container">
    <el-alert title="文件下发功能需要目标主机配置免密登录"
              type="info"
              effect="light"
              :closable="false">
    </el-alert>

    <el-dialog title="文件上传"
               :visible.sync="centerDialogVisible"
               width="30%"
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
          <el-upload class="upload-demo"
                     :http-request="handleFile"
                     :multiple="false"
                     :limit="1"
                     drag
                     action="sss"
                     clearFiles
                     :on-exceed="handleExceed"
                     :file-list="fileList"
                     :before-upload="beforeAvatarUpload">
            <i class="el-icon-upload"></i>
            <div class="el-upload__text">将文件拖到此处，或
              <em>点击上传</em>
            </div>
            <div class="el-upload__tip"
                 slot="tip">仅支持 properties|txt|sql|sh|py|xml|yaml|cfg|ini|config|xmind|data|rmi|conf|json|toml 结尾的文件上传，且不超过5MB</div>
          </el-upload>
          <div class="upload_form_item">
            <el-form-item label="分发时间"
                          prop="plan_time">
              <el-col :span="17">
                <el-date-picker type="datetime"
                                :picker-options="pickerOptions"
                                placeholder="选择日期"
                                v-model="form.plan_time"
                                style="width: 100%;"></el-date-picker>
              </el-col>
            </el-form-item>
          </div>
        </el-form>
      </div>
      <span slot="footer"
            class="dialog-footer">
        <el-button @click="resetForm('form')">取 消</el-button>
        <el-button type="primary"
                   @click="uploadDoc('form')">确 定</el-button>
      </span>
    </el-dialog>

    <el-dialog title="文件分发"
               :visible.sync="DistributeDialogVisible"
               width="50%"
               destroy-on-close
               :close-on-click-modal=false
               :close-on-press-escape=false
               @close="resetDistribeForm('distributeForm')">
      <div class="dialog-form">
        <el-form ref="distributeForm"
                 :model="distributeForm"
                 :rules="distributeRules"
                 label-width="100px">
          <el-form-item label="文件名"
                        prop="name">
            <el-input type="text"
                      v-model="distributeForm.name"
                      disabled
                      style="width: 91%"></el-input>
          </el-form-item>
          <el-form-item label="分发实例"
                        prop="instance">
            <el-transfer filterable
                         :titles="['可用实例', '已选实例']"
                         filter-placeholder="请输入搜索内容"
                         v-model="distributeForm.instance"
                         @change="handleChange"
                         :data="instanceData">
            </el-transfer>
          </el-form-item>
          <el-form-item label="目标路径"
                        prop="path">
            <el-input v-model="distributeForm.path"
                      placeholder="请输入"
                      style="width: 91%"></el-input>
          </el-form-item>
          <el-form-item label="文件权限"
                        prop="permisson">
            <el-radio-group v-model="distributeForm.permisson">
              <el-radio label="755">755</el-radio>
              <el-radio label="744">744</el-radio>
              <el-radio label="700">700</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="文件属主"
                        prop="ownner">
            <el-radio-group v-model="distributeForm.ownner">
              <el-radio label="root">root</el-radio>
              <el-radio label="admin">admin</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer"
            class="dialog-footer">
        <el-button @click="resetDistribeForm('distributeForm')">取 消</el-button>
        <el-button type="primary"
                   @click="distribeFile('distributeForm')">确 定</el-button>
      </span>
    </el-dialog>

    <el-form :inline="true"
             :model="formInline"
             class="demo-form-inline">
      <el-form-item label="文件名">
        <el-input v-model="formInline.name"
                  placeholder="请输入" />
      </el-form-item>
      <el-form-item label="上传日期">
        <el-date-picker v-model="formInline.plan_time"
                        type="date"
                        placeholder="选择日期" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary"
                   @click="onSearch">搜索</el-button>
      </el-form-item>
      <el-form-item>
        <el-button type="primary"
                   @click="centerDialogVisible = true">上传文件</el-button>
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
      <el-table-column label="文件名"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column label="分发状态"
                       align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.status }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.job_status }}
        </template>
      </el-table-column>
      <el-table-column label="分发时间"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.plan_time }}
        </template>
      </el-table-column>
      <el-table-column label="备注"
                       align="center"
                       width="140"
                       show-overflow-tooltip>
        <template slot-scope="scope">
          {{ FormatValue(scope.row.message) }}
        </template>
      </el-table-column>
      <el-table-column label="创建时间"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.create_time }}
        </template>
      </el-table-column>
      <el-table-column label="操作者"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.operator }}
        </template>
      </el-table-column>
      <el-table-column label="参数"
                       align="center"
                       width="150"
                       show-overflow-tooltip>
        <template slot-scope="scope">
          {{ scope.row.payload }}
        </template>
      </el-table-column>
      <el-table-column align="center"
                       prop="created_at"
                       label="操作"
                       width="300">
        <template slot-scope="scope">
          <el-button size="mini"
                     type="primary"
                     icon="el-icon-bottom"
                     round
                     @click="handleDownload(scope.$index, scope.row)">下载</el-button>
          <el-button v-if="distributeFile(scope.row)"
                     size="mini"
                     type="primary"
                     icon="el-icon-share"
                     round
                     @click="handleDistribute(scope.$index, scope.row)">分发</el-button>
          <el-button v-else-if="rollbackFile(scope.row)"
                     size="mini"
                     type="primary"
                     icon="el-icon-d-arrow-left"
                     round
                     @click="handleRollback(scope.$index, scope.row)">恢复</el-button>
          <el-button v-if="deleteFile(scope.row)"
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
  </div>
</template>

<script>
import { getDocument, uploadDocument, downloadDocument, distributeDocument, restoreDocument, deleteDocument } from '@/api/document'
import { FormatDateTime, FormatValue, FormatDate } from '@/utils/index'
import { getEcs } from '@/api/cmdb'
import { setTimeout } from 'timers';
export default {
  data () {
    var checkIntance = (rule, value, callback) => {
      if (value.length < 1) {
        return callback(new Error('实例不能为空'));
      }
      callback();
    };
    return {
      list: null,
      listLoading: true,
      formInline: {
        name: '',
        plan_time: ''
      },
      dialogRules: {
        plan_time: [{ required: true, trigger: 'blur', message: '时间不能为空' }]
      },
      form: {
        plan_time: ''
      },
      distributeForm: {
        name: '',
        instance: [],
        path: '',
        permisson: '',
        ownner: ''
      },
      distributeRules: {
        name: [{ required: true, trigger: 'blur', message: '文件名不能为空' }],
        instance: [{ required: true, trigger: 'blur', validator: checkIntance, type: 'array' }],
        path: [{ required: true, trigger: 'blur', message: '路径不能为空' }],
        permisson: [{ required: true, trigger: 'blur', message: '文件权限未选择' }],
        ownner: [{ required: true, trigger: 'blur', message: '文件属主未选择' }]
      },
      pickerOptions: {
        disabledDate (time) {
          const date = new Date();
          return time.getTime() < (date.getTime() - 3600 * 1000 * 24)
        }
      },
      value: true,
      centerDialogVisible: false,
      DistributeDialogVisible: false,
      fileList: [],
      instanceData: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      rowId: '',
      shareFile: ["sql", "sh", "conf", "py", "properties", "xml", "yaml", "txt"],
      allowUploadFile: ["properties", "txt", "sql", "sh", "py", "xml", "yaml", "cfg", "ini", "config", "xmind", "data", "rmi", "conf", "json", "toml"]
    }
  },
  created () {
    this.fetchData()
    this.getInstance()
  },
  methods: {
    getInstance () {
      getEcs().then(response => {
        let results = response.data
        for (let i = 0; i < results.length; i++) {
          this.instanceData.push({
            key: results[i].id,
            label: results[i].hostname
          })
        }
      }).catch(error => {
        console.log(error)
      })
    },
    fetchData () {
      this.listLoading = true
      getDocument().then(response => {
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
        deleteDocument(row.id).then(response => {
          for (var i = 0; i < this.list.length; i++) {
            if (this.list[i].id === row.id) {
              this.list.splice(i, 1)
            }
          }
          this.total -= 1
          this.$message({
            type: 'success',
            message: '删除成功!'
          });
        }).catch(error => {
          console.log(error)
          // this.$message({
          //   type: 'error',
          //   message: '删除失败!'
          // });
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    },
    beforeAvatarUpload (file) {
      const isAllowFile = this.allowUploadFile.indexOf(file.name.split('.')[file.name.split('.').length - 1]) !== -1;
      console.log('allow', isAllowFile)
      const isLt2M = file.size / 1024 / 1024 < 5;

      if (!isAllowFile) {
        this.$message.error('上传文件格式不被允许!');
      }

      if (!isLt2M) {
        this.$message.error('上传文件大小不能超过 5MB!');
      }
      return isAllowFile && isLt2M
    },
    handleFile (fileobj) {
      console.log('fileobj', fileobj)
      this.fileList.push(fileobj.file)
    },
    handleExceed (files, fileList) {
      this.$message.warning(`最多上传 ${files.length} 个文件`)
    },
    uploadDoc (formName) {
      let that = this
      that.$refs[formName].validate((valid) => {
        if (valid) {
          console.log(that.fileList[0])
          let form = that.$refs[formName].$el
          let formData = new FormData(form)

          formData.append('plan_time', FormatDateTime(this.form.plan_time))
          formData.append('file', that.fileList[0])
          uploadDocument(formData).then(response => {
            if (response.status === 200) {
              that.centerDialogVisible = false
              this.$message.success('文件上传成功')
              that.fileList = []
              setTimeout(() => {
                this.fetchData()
              }, 2000)
            } else {
              this.$message.error('文件上传失败')
            }
          }).catch(error => {
            console.log(error)
            // this.$message.error(JSON.stringify(error.response.data))
          })
        } else {
          console.log('error')
        }
      })
    },
    resetForm (formName) {
      this.$refs[formName].resetFields();
      this.fileList = []
      this.centerDialogVisible = false
    },
    onSearch () {
      getDocument({
        name: this.formInline.name,
        create_time: FormatDate(this.formInline.plan_time)
      }).then(response => {
        this.list = response.data.results
        this.total = response.data.count
      }).catch(error => {
        console.log(error)
      })
    },
    handleSizeChange: function (pageSize) { // 每页条数切换
      this.pageSize = pageSize
      this.findPage(this.currentPage, this.pageSize);
    },
    handleCurrentChange: function (currentPage) { // 页码切换
      this.currentPage = currentPage
      this.findPage(this.currentPage, this.pageSize)
    },
    findPage (pageCode, pageSize) {
      getDocument({ page: pageCode, page_size: pageSize }).then(response => {
        this.list = response.data.results
        this.total = response.data.count
      }).catch(error => {
        console.log(error)
      })
    },
    checkStatus (value) {
      if (value === 0) {
        return '已上传待确认'
      }
      return '已确认'
    },
    FormatValue,
    distributeFile: function (row) {
      if (row.status === '未设置' && this.shareFile.indexOf(row.name.split('.')[row.name.split('.').length - 1]) !== -1 || row.status === '已执行' && row.job_status === '失败') {
        return true
      }
      return false
    },
    rollbackFile: function (row) {
      if (row.job_status == '成功' && !row.message) {
        return true
      }
      return false
    },
    deleteFile: function (row) {
      if (row.status === '未设置' && row.job_status === '未执行' || row.status === '已执行' && row.job_status === '失败') {
        return true
      }
      return false
    },
    handleDownload (index, row) {
      downloadDocument(row.id).then(response => {
        let blob = new Blob([response.data]);
        if (window.navigator.msSaveOrOpenBlob) {
          navigator.msSaveBlob(blob, row.name);
        } else {
          let link = document.createElement("a");
          let evt = document.createEvent("HTMLEvents");
          evt.initEvent("click", false, false);
          link.href = URL.createObjectURL(blob);
          link.download = row.name;
          link.style.display = "none";
          document.body.appendChild(link);
          link.click();
          window.URL.revokeObjectURL(link.href);
        }
      }).catch(error => {
        console.log(error.response)
      })
    },
    handleDistribute (index, row) {
      this.DistributeDialogVisible = true
      this.distributeForm.name = row.name
      this.rowId = row.id
    },
    handleRollback (index, row) {
      this.$confirm('你真的要恢复 ' + row.name + ' 么？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        restoreDocument(row.id).then(response => {
          this.$message({
            type: 'success',
            message: '操作成功!'
          });
          this.fetchData()
        }).catch(error => {
          console.log(error)
          // this.$message({
          //   type: 'error',
          //   message: JSON.stringify(error.response.data)
          // });
        })
      }).catch(() => { })
    },
    handleChange (value, direction, movedKeys) {
      console.log(value, direction, movedKeys)
    },
    distribeFile (formName) {
      // let that = this
      let data = {}
      this.$refs[formName].validate((valid) => {
        if (valid) {
          console.log('valid')
          let payload = ''
          let ownner = this.distributeForm.ownner
          if (ownner === 'root') {
            payload = {
              "commands": {
                "permission": this.distributeForm.permisson
              },
              "path": this.distributeForm.path,
              "servers": this.distributeForm.instance,
            }
          } else {
            payload = {
              "commands": {
                "owner": true,
                "group": 1,
                "permission": this.distributeForm.permisson
              },
              "path": this.distributeForm.path,
              "servers": this.distributeForm.instance,
            }
          }

          distributeDocument(this.rowId, { payload: payload }).then(response => {
            if (response.status === 200) {
              this.DistributeDialogVisible = false
              this.$message.success('分发文件配置成功')
              setTimeout(() => {
                this.fetchData()
              }, 2000)
            } else {
              this.$message.error('分发配置失败')
            }
          }).catch(error => {
            console.log(error)
          })
        } else {
          console.log('error')
        }
      })
    },
    resetDistribeForm (formName) {
      this.DistributeDialogVisible = false
      this.$refs[formName].resetFields();
    }
  }
}
</script>
<style scoped>
/* .dialogbody {
  margin-left: 15%;
} */

.dialogbody {
  text-align: center;
}
.pagination {
  margin: 20px 0;
  text-align: right;
}
.upload-demo /deep/ .el-upload-dragger {
  height: 110px;
}
.upload-demo .el-upload__tip {
  color: #f56c6c;
  width: 360px;
  line-height: initial;
  margin-left: auto;
  margin-right: auto;
  text-align: left;
}
.el-upload-dragger .el-icon-upload {
  margin: 10px 0 10px 0;
}
.upload-demo /deep/ .el-upload-list {
  display: inline-block;
  width: 360px;
}

.el-upload-list >>> .el-upload-list__item-name {
  float: left;
}
.el-transfer >>> .el-transfer-panel {
  width: 320px;
}
.upload_form_item {
  margin-top: 20px;
  display: inline-block;
  width: 400px;
}

div >>> .el-form-item__content {
  line-height: 1;
}
</style>
<style>
.el-alert {
  margin: 0 0 15px 0;
}
</style>