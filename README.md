------

## 系统简介

FL(falcon horizontal line) 隼的视平线-风火轮系统，是奥琪科技（https://www.ooqi.cn）根据业务需要自行研发，提供高效交付效率的综合管理平台。平台集公有云（目前仅支持阿里云）资源管理，任务编排，工作流，版本控制，业务监控等功能。抽象底层资源，为开发，运维，测试，PM提供综合支撑能力。

------



## 开发技术

| 后端                      | 前端             | 开源组        |
| ------------------------- | ---------------- | ------------- |
| Python3.6                 | Vue2.6.10        | RabbitMQ      |
| djangorestframework3.10.3 | Element-UI       | MySQL5.6      |
| Django2.2                 | Element-UI-admin | Inotify-tools |
|                           |                  | vsftpd        |
|                           |                  | ETCD          |



- `Python` https://www.python.org/downloads/windows/
- `djangorestframework` https://www.django-rest-framework.org/
- `Django` https://docs.djangoproject.com/en/dev/releases/2.2/
- `vue` https://cn.vuejs.org/v2/guide/
- `Element-UI` https://element.eleme.cn/#/zh-CN
- `RabbitMQ` https://www.rabbitmq.com/#getstarted
- `MySQL` https://dev.mysql.com/doc/
- `inotify-tools` https://github.com/rvoicilas/inotify-tools
- `vsftpd` https://security.appspot.com/vsftpd.html
- `ETCD` https://github.com/etcd-io/etcd

------



## 系统架构图

![i](fhl.png)

> 1. 阿里云基础设施
> 2. 调度中心，同步核心，工作流，通知渠道
> 3. 权限，编排，文件传输，命令，版本控制
> 4. 业务配置，业务任务，业务日志
> 5. 可视化，通知，告警，审计等
>
> 

------



## 已完成开源模块

- 系统配置，包括阿里云账号信息配置（同步阿里云资源）、系统名/LOGO 自定义。
- 用户管理，包括权限、部门管理等模块。
- 资产管理，在系统配置中添加阿里云账号信息之后， 系统会同步 ECS、RDS 和 SLB 资源。ECS 可与项目绑定。
- 项目管理。支持项目的添加、修改与删除操作。 可在资产管理中 绑定 ECS。
- 文件管理，支持文件批量下发

## 安装方式

### 一、源代码安装

首先需要安装 MySQL5.6 和 RabbitMQ，之后再用 `pipenv` 安装相关依赖：

```shell
pipenv install
```

配置在 `settings` 中，可根据需要自行修改。修改配置中的数据库配置，比如：

```python
#Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'you-database-name',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'host',
        'PORT': 3306,
    }
}

# ETCD
ETCD_HOST_URL = '127.0.0.1'
ETCD_PORT = 2379
ETCD_AUTO_BACKUP_DIR = 'distribute_config_auto_backup'

# RabbitMQ
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
BROKER_URL = 'amqp://your-mq-user:your-mq-password@your-mq-host:5672/ams'  
CELERY_RESULT_BACKEND = 'amqp://your-mq-user:your-mq-password@your-mq-host:5672/ams'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERYD_MAX_TASKS_PER_CHILD = 3
CELERY_CONSUMER_MQ_BROKER_URL = 'amqp://our-mq-user:your-mq-password@your-mq-host:5672'

```

创建对应的数据库之后在终端下执行以下命令创建相应的表：

```shell
python manage.py makemigrations
python manage.py migrate
```

启动`tethys`服务

```shell
python manage.py runserver
```

访问`tethys`服务,浏览器打开 http://127.0.0.1:8000/ 即可看到效果。

### 二、Docker镜像安装

docker-compose.yml


------



## 用户与权限控制

权限类型由系统预定义， 自定义的模块权限需要将模块名存入数据库中 （在 Django 交互式命令行中， 执行 account/init_permission.py 中 main 函数来导入默认权限）

用户与部门管理，部门再关联具体的权限。

```mysql
use `database_name`;
source accounting/init_permission.py;
```

## 功能介绍

### 一、系统管理

- 阿里云AK配置
- 服务器账户密码配置

### 二、用户管理

- 部门管理
- 权限管理
- 人员管理

### 三、资产管理

### 四、项目管理

### 五、文件管理

## 安装及运行FAQ

### 1. 400 状态码

该状态码表示输入数据与服务器上要求的不一致或是输入数据有误。 如登录页面输入错误的用户名或密码显示的 `Unable to log in with provided credentials`、 应用批量绑定 ECS 失败、 删除部门/组时，该部门、组有关联用户等。

### 2. 401 状态码

该状态码表示未登录，请登录后重试。前端已设置自动跳转登录页面。

### 3. 403 状态码

该状态码表示用户无权访问该页面，设置相应的权限后即可。

### 4. 500 以上状态码

该状态码表示服务器内部错误，需要查看服务器具体日志定位错误。如文件管理中上传文件失败、下载文件失败等。