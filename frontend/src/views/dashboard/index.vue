<template>
  <div class="dashboard-container">
    <div class="dashboard-text">欢迎使用{{ title || defaultTitle }} </div>
    <div class="content">

      <h4>功能列表：</h4>
      <ul>
        <li class="list"
            v-for="(todo, index) in todos"
            :key="index">
          {{ todo }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex';
export default {
  data () {
    return {
      defaultTitle: '应用管理系统',
      todos: [
        '阿里云ECS、RDS、SLB资源同步',
        '项目管理',
        '资源管理',
        '文件管理',
        '用户管理',
        '系统配置'
      ]
    }
  },
  computed: {
    ...mapGetters([
      'title'
    ])
    //     ...mapGetters('settings', [
    //   'title'
    // ])
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
  &-container {
    margin: 30px;
  }
  &-text {
    font-size: 30px;
    line-height: 46px;
  }
}
.content {
  margin: 15px;
}
.list {
  margin: 5px 0 5px 0;
}
</style>
