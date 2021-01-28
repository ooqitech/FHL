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
      <el-table-column label="权限名称"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column label="描述"
                       align="center">
        <template slot-scope="scope">
          {{ scope.row.desc }}
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
import { getPermissions, DeletePermissions, AddPermissions } from '@/api/account.js'
import { constants } from 'fs';
import { setTimeout } from 'timers';
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
      total: 0,
      currentPage: 1,
      pageSize: 10,
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      this.listLoading = true
      getPermissions().then(response => {
        this.list = response.data.results
        this.total = response.data.count
        this.listLoading = false
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
      getPermissions({ page: pageCode, page_size: pageSize }).then(response => {
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
