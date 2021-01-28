<template>
  <div class="login-wrap">
    <div class="ms-login">
      <div class="ms-title">Tethys</div>
      <el-form ref="loginForm"
               :model="loginForm"
               :rules="loginRules"
               label-width="0px"
               class="ms-content"
               auto-complete="on"
               label-position="left">
        <el-form-item prop="username">
          <el-input ref="username"
                    v-model="loginForm.username"
                    placeholder="用户名"
                    name="username"
                    type="text"
                    tabindex="1"
                    auto-complete="on">
            <el-button slot="prepend"
                       icon="el-icon-user-solid" />
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input :key="passwordType"
                    ref="password"
                    v-model="loginForm.password"
                    :type="passwordType"
                    placeholder="密码"
                    name="password"
                    tabindex="2"
                    auto-complete="on"
                    @keyup.enter.native="handleLogin">
            <el-button slot="prepend"
                       icon="el-icon-unlock" />
          </el-input>
        </el-form-item>
        <div class="login-btn">
          <el-button :loading="loading"
                     type="primary"
                     @click.native.prevent="handleLogin">登陆</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
import { getSystem } from '@/api/setting'
export default {
  name: 'Login',
  data () {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [{ required: true, trigger: 'blur', message: '请输入用户名' }],
        password: [{ required: true, trigger: 'blur', message: '请输入密码' }]
      },
      loading: false,
      passwordType: 'password',
      redirect: undefined
    }
  },
  watch: {
    $route: {
      handler: function (route) {
        this.redirect = route.query && route.query.redirect
      },
      immediate: true
    }
  },
  methods: {
    handleLogin () {
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          this.loading = true
          this.$store.dispatch('user/login', this.loginForm).then(() => {

            setTimeout(() => {
              this.$router.push({ path: this.redirect || '/' })
            }, 2000)
            this.loading = false
            this.$message({
              message: '登录成功',
              type: 'success',
              duration: 2000
            })

          }).catch((error) => {
            this.loading = false
          })
          this.$store.dispatch('settings/getSystem')
        } else {
          console.log('error submit!!')
          return false
        }
      })
    }
  }
}
</script>

<style lang="scss">
.login-wrap {
  position: relative;
  width: 100%;
  height: 100%;
  background-image: url(../../assets/img/login.jpg);
  background-size: 100%;
}
.ms-title {
  width: 100%;
  line-height: 50px;
  text-align: center;
  font-size: 20px;
  color: #fff;
  border-bottom: 1px solid #ddd;
}
.ms-login {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 350px;
  margin: -190px 0 0 -175px;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.3);
  overflow: hidden;
}
.ms-content {
  padding: 30px 30px;
}
.login-btn {
  text-align: center;
}
.login-btn button {
  width: 100%;
  height: 36px;
  margin-bottom: 10px;
}
.login-tips {
  font-size: 12px;
  line-height: 30px;
  color: #fff;
}
</style>
