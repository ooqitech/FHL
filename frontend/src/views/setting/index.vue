<template>
  <div class="app-container">
    <el-dialog title="添加阿里云配置"
               :visible.sync="aliDialogVisible"
               width="30%"
               center
               destroy-on-close
               @close="resetForm('form')">
      <div class="dialog-form">
        <el-form ref="form"
                 :model="form"
                 :rules="dialogRules"
                 label-width="150px"
                 class="dialogbody">
          <el-form-item label="AccessKeyId"
                        prop="AccessKeyId">
            <el-input v-model="form.AccessKeyId"
                      style="width: 71%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item label="AccessKeySecret"
                        prop="AccessKeySecret">
            <el-input v-model="form.AccessKeySecret"
                      style="width: 71%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item label="Region"
                        prop="Region">
            <el-input v-model="form.Region"
                      style="width: 71%"
                      autocomplete="off"></el-input>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer"
            class="dialog-footer">
        <el-button @click="resetForm('form')">取 消</el-button>
        <el-button type="primary"
                   @click="AddAliyunForm('form')">确 定</el-button>
      </span>
    </el-dialog>

    <el-dialog title="添加系统配置"
               :visible.sync="systemDialogVisible"
               width="30%"
               destroy-on-close
               :close-on-click-modal=false
               :close-on-press-escape=false
               @close="resetSysForm('sysform')">
      <div class="dialog">
        <el-form ref="sysform"
                 :model="sysform"
                 :rules="sysdialogRules"
                 label-width="150px"
                 class="sysdialogbody">
          <el-upload class="upload-demo"
                     :http-request="handleFile"
                     :multiple="false"
                     :limit="1"
                     drag
                     action="#"
                     clearFiles
                     :on-exceed="handleExceed"
                     :file-list="fileList"
                     :before-upload="beforeAvatarUpload">
            <i class="el-icon-upload"></i>
            <div class="el-upload__text">将文件拖到此处，或
              <em>点击上传</em>
            </div>
            <div class="el-upload__tip"
                 slot="tip">仅支持 png 文件上传, 图片尺寸 150 x 150</div>
          </el-upload>
          <div class="upload_form_item">
            <el-form-item label="Title"
                          prop="title">
              <el-input v-model="sysform.title"
                        style="width: 80%"
                        autocomplete="off"></el-input>
            </el-form-item>
          </div>
        </el-form>
      </div>
      <span slot="footer"
            class="dialog-footer">
        <el-button @click="resetSysForm('sysform')">取 消</el-button>
        <el-button type="primary"
                   @click="uploadLogo('sysform')">确 定</el-button>
      </span>
    </el-dialog>

    <!-- <el-dialog title="添加ssh配置"
               :visible.sync="sshDialogVisible"
               width="30%"
               center
               destroy-on-close
               @close="resetForm('sshform')">
      <div class="dialog-form">
        <el-form ref="sshform"
                 :model="sshform"
                 :rules="dialogRules"
                 label-width="150px"
                 class="dialogbody">
          <el-form-item label="IP"
                        prop="ip">
            <el-input v-model="sshform.ip"
                      style="width: 71%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item label="用户名"
                        prop="username">
            <el-input v-model="sshform.username"
                      style="width: 71%"
                      autocomplete="off"></el-input>
          </el-form-item>
          <el-form-item label="密码"
                        prop="password">
            <el-input v-model="sshform.password"
                      style="width: 71%"
                      autocomplete="off"></el-input>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer"
            class="dialog-footer">
        <el-button @click="resetSshForm('sshform')">取 消</el-button>
        <el-button type="primary"
                   @click="AddSshForm('sshform')">确 定</el-button>
      </span>
    </el-dialog> -->

    <!-- <el-dialog :visible.sync="dialogVisible">
      <img width="100%"
           :src="dialogImageUrl"
           alt="">
    </el-dialog> -->

    <div class="setting">
      <el-tabs v-model="activeName"
               @tab-click="handleClick"
               class="setting-tabs">
        <el-tab-pane label="阿里云配置"
                     name="aliyun">
          <el-form :inline="true">
            <el-form-item>
              <el-button type="primary"
                         size="small"
                         @click="handleAliyunAdd">添加配置</el-button>
              <el-tooltip class="item"
                          effect="dark"
                          content="AccessKeyId需要配置ECS、RDS、SLB权限，否则同步会失败；可以添加多个AccessKeyId，同步多个账号资源"
                          placement="right">
                <i style="margin-left: 10px"
                   class="el-icon-question"></i>
              </el-tooltip>
            </el-form-item>
          </el-form>
          <el-table v-loading="aliLoading"
                    :data="aliyunlist"
                    element-loading-text="Loading"
                    border
                    fit
                    highlight-current-row>
            <el-table-column align="center"
                             label="ID">
              <template slot-scope="scope">
                {{ scope.row.id }}
              </template>
            </el-table-column>
            <el-table-column label="key"
                             align="center">
              <template slot-scope="scope">
                {{ scope.row.key }}
              </template>
            </el-table-column>
            <el-table-column label="secret"
                             align="center">
              <template slot-scope="scope">
                {{ scope.row.secret }}
              </template>
            </el-table-column>
            <el-table-column label="region"
                             align="center">
              <template slot-scope="scope">
                {{ scope.row.region }}
              </template>
            </el-table-column>
            <el-table-column label="创建时间"
                             align="center">
              <template slot-scope="scope">
                {{ scope.row.create_time }}
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
        </el-tab-pane>
        <el-tab-pane label="系统配置"
                     name="system">
          <el-form :inline="true">
            <el-form-item>
              <el-button type="primary"
                         size="small"
                         @click="handleSystemAdd">添加配置</el-button>
              <el-tooltip class="item"
                          effect="dark"
                          content="添加配置将覆盖现有的配置，配置重新登录生效"
                          placement="right">
                <i style="margin-left: 10px"
                   class="el-icon-question"></i>
              </el-tooltip>
            </el-form-item>
          </el-form>
          <el-table v-loading="sysLoading"
                    :data="syslist"
                    element-loading-text="Loading"
                    border
                    fit
                    highlight-current-row>
            <el-table-column align="center"
                             label="ID">
              <template slot-scope="scope">
                {{ scope.row.id }}
              </template>
            </el-table-column>
            <el-table-column label="title"
                             align="center">
              <template slot-scope="scope">
                {{ scope.row.name }}
              </template>
            </el-table-column>
            <el-table-column label="logo"
                             align="center">
              <template slot-scope="scope">
                {{ scope.row.logo }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <!-- <el-tab-pane label="SSH配置"
                     name="SSH">
          <el-form :inline="true">
            <el-form-item>
              <el-button type="primary"
                         size="small"
                         @click="handleSshAdd">添加配置</el-button>
              <el-tooltip class="item"
                          effect="dark"
                          content="SSH配置用于文件同步使用"
                          placement="right">
                <i style="margin-left: 10px"
                   class="el-icon-question"></i>
              </el-tooltip>
            </el-form-item>
          </el-form>
          <el-table v-loading="sshLoading"
                    :data="sshlist"
                    element-loading-text="Loading"
                    border
                    fit
                    highlight-current-row>
            <el-table-column align="center"
                             label="ID">
              <template slot-scope="scope">
                {{ scope.row.id }}
              </template>
            </el-table-column>
            <el-table-column label="主机"
                             align="center">
              <template slot-scope="scope">
                {{ scope.row.hostname }}
              </template>
            </el-table-column>
            <el-table-column label="用户名"
                             align="center">
              <template slot-scope="scope">
                {{ scope.row.username }}
              </template>
            </el-table-column>
            <el-table-column label="创建时间"
                             align="center">
              <template slot-scope="scope">
                {{ scope.row.create_time }}
              </template>
            </el-table-column>
            <el-table-column align="center"
                             label="操作"
                             width="200">
              <template slot-scope="scope">
                <el-button size="mini"
                           type="danger"
                           icon="el-icon-delete"
                           round
                           @click="handleSshDelete(scope.$index, scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane> -->
      </el-tabs>
    </div>

  </div>
</template>

<script>
import { getAliyunConfig, getSystem, AddAliyun, AddSystem, DeleteAliyun, AddSystemSetting, getSshConfig, DeleteSshConfig, AddSshConfig } from '@/api/setting'
import { setTimeout } from 'timers';
export default {
  data () {
    var checkIP = (rule, value, callback) => {
      if (!value) {
        return callback(new Error('IP地址不能为空'));
      } else {
        const reg = /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/
        console.log(reg.test(value));
        if (reg.test(value)) {
          callback();
        } else {
          return callback(new Error('请输入正确的IP地址'));
        }
      }
    };
    return {
      activeName: 'aliyun',
      aliyunlist: null,
      aliLoading: true,
      syslist: null,
      sysLoading: true,
      sshlist: null,
      sshLoading: true,
      aliDialogVisible: false,
      systemDialogVisible: false,
      sshDialogVisible: false,
      dialogVisible: false,
      dialogImageUrl: '',
      disabled: false,
      sysform: {
        title: ''
      },
      sysdialogRules: {
        title: [{ required: true, trigger: 'blur', message: 'title不能为空' }]
      },
      fileList: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      dialogRules: {
        AccessKeyId: [{ required: true, trigger: 'blur', message: 'AccessKeyId不能为空' }],
        AccessKeySecret: [{ required: true, trigger: 'blur', message: 'AccessKeySecret不能为空' }],
        Region: [{ required: true, message: 'Region不能为空', trigger: 'blur' }],
        ip: [{ required: true, trigger: 'blur', validator: checkIP }],
        username: [{ required: true, trigger: 'blur', message: '用户名不能为空' }],
        password: [{ required: true, trigger: 'blur', message: '密码不能为空' }],
      },
      form: {
        AccessKeyId: '',
        AccessKeySecret: '',
        Region: ''
      },
      sshform: {
        ip: '',
        username: '',
        password: ''
      }
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      this.listLoading = true
      getAliyunConfig({ per_page: this.pageSize, page: this.currentPage }).then(response => {
        this.aliyunlist = response.data.results
        this.aliLoading = false
      }).catch(error => {
        console.log(error)
      })
    },
    getSysData () {
      getSystem().then(response => {
        this.syslist = response.data.results
        this.sysLoading = false
      }).catch(error => {
        console.log(error)
      })
    },
    getSshData () {
      getSshConfig().then(response => {
        this.sshlist = response.data.results
        this.sshLoading = false
      }).catch(error => {
        console.log(error)
      })
    },
    handleSshAdd () {
      this.sshDialogVisible = true
    },
    handleAliyunAdd () {
      this.aliDialogVisible = true
    },
    resetForm (formName) {
      this.$refs[formName].resetFields();
      this.aliDialogVisible = false
    },
    handleSystemAdd () {
      this.systemDialogVisible = true
    },
    uploadLogo (formName) {
      let that = this
      that.$refs[formName].validate((valid) => {
        if (valid) {
          // console.log(that.fileList[0])
          let form = that.$refs[formName].$el
          let formData = new FormData(form)
          formData.append('name', this.sysform.title)
          formData.append('logo', that.fileList[0])
          AddSystemSetting(formData).then(response => {
            if (response.status === 201) {
              that.systemDialogVisible = false
              this.$message.success('配置设置成功')
              that.fileList = []
              setTimeout(() => {
                this.fetchData()
              }, 2000)
            } else {
              this.$message.error('配置设置失败')
            }
          }).catch(error => {
            if (error.response.hasOwnProperty('data') === true) {
              this.$message.error(error.response.data.non_field_errors[0])
            }
          })
        } else {
          console.log('error')
        }
      })
    },
    resetSysForm (formName) {
      this.$refs[formName].resetFields();
      this.fileList = []
      this.systemDialogVisible = false
    },
    resetSshForm (formName) {
      this.$refs[formName].resetFields();
      this.sshDialogVisible = false
    },
    beforeAvatarUpload (file) {
      const isAllowFile = file.type === 'image/png';
      console.log('allow', isAllowFile)
      const isLt2M = file.size / 1024 < 50;

      if (!isAllowFile) {
        this.$message.error('上传图片只能是PNG格式!');
      }

      if (!isLt2M) {
        this.$message.error('上传文件大小不能超过 50KB !');
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
    AddAliyunForm (formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          let data = {
            "key": this.form.AccessKeyId,
            "secret": this.form.AccessKeySecret,
            "region": this.form.Region,
          }
          AddAliyun(data).then(response => {
            this.aliDialogVisible = false
            this.$message.success('添加成功')
            setTimeout(() => {
              this.fetchData()
            }, 1000)
          }).catch(error => {
            console.log(error)
          })
        } else {
          console.log('error')
        }
      })
    },
    AddSshForm (formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          let data = {
            "hostname": this.sshform.ip,
            "username": this.sshform.username,
            "password": this.sshform.password,
          }
          AddSshConfig(data).then(response => {
            this.sshDialogVisible = false
            this.$message.success('添加成功')
            setTimeout(() => {
              this.getSshData()
            }, 1000)
          }).catch(error => {
            console.log(error)
          })
        } else {
          console.log('error')
        }
      })
    },
    handleDelete (index, row) {
      this.$confirm('你真的要删除 ' + row.key + ' 么？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        DeleteAliyun(row.id).then(response => {
          for (var i = 0; i < this.aliyunlist.length; i++) {
            if (this.aliyunlist[i].id === row.id) {
              this.aliyunlist.splice(i, 1)
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
      }).catch(() => { })
    },
    handleSshDelete (index, row) {
      this.$confirm('你真的要删除 ' + row.hostname + ' 么？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        DeleteSshConfig(row.id).then(response => {
          for (var i = 0; i < this.sshlist.length; i++) {
            if (this.sshlist[i].id === row.id) {
              this.sshlist.splice(i, 1)
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
      }).catch(() => { })
    },
    handleClick (tab, event) {
      if (tab.name === 'system') {
        this.getSysData()
      } else {
        this.getSshData()
      }
    },
    handlePictureCardPreview (file) {
      this.dialogImageUrl = file.url;
      this.dialogVisible = true;
    },
  }
}
</script>
<style scoped>
.sysdialogbody {
  text-align: center;
}
.setting {
  border: 1px solid #ebebeb;
  border-radius: 3px;
  transition: 0.2s;
}
.setting-tabs {
  padding: 24px;
}
.tabs-table {
  margin-top: 22px;
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
  text-align: left;
}

.el-upload-list >>> .el-upload-list__item-name {
  float: left;
}

.el-transfer >>> .el-transfer-panel {
  width: 320px;
}

div >>> .el-form-item__content {
  line-height: 1;
  text-align: left;
}
</style>
