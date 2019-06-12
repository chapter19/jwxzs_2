一、替换阿里云homebrew加速下载
cd "$(brew --repo)"

git remote set-url origin https://mirrors.aliyun.com/homebrew/brew.git

cd "$(brew --repo)/Library/Taps/homebrew/homebrew-core"

git remote set-url origin https://mirrors.aliyun.com/homebrew/homebrew-core.git

echo 'export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.aliyun.com/homebrew/homebrew-bottles' >> ~/.bash_profile

source ~/.bash_profile


二、安装redis
brew install redis

开启服务
redis-server /usr/local/etc/redis.conf

打开客户端
redis-cli

关闭服务
SHUTDOWN

设置密码
CONFIG SET requirepass "1"
quit

验证密码
redis-cli
auth 1

查看所有键
keys *


三、安装rabbitmq
brew install rabbitmq

开启服务
brew services start rabbitmq

后台运行
sudo rabbitmq-server -detached

停止服务
sudo rabbitmqctl stop

#添加用户（先不管）
sudo rabbitmqctl add_user myuser mypassword
sudo rabbitmqctl add_vhost myvhost
sudo rabbitmqctl set_user_tags myuser mytag
sudo rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"

四、安装neo4j desktop
开启服务
导入数据




运行项目

redis-server /usr/local/etc/redis.conf
新开一个
brew services start rabbitmq
新开一个
sudo rabbitmq-server 
新开一个
cd /Users/vccccccc/PycharmProjects/jwxzs_2 && celery -A jwxzs_2 worker -B -l info
新开一个
python manage.py runserver



#cd /Users/vccccccc/PycharmProjects/jwxzs_2 && workon jwxzs_3.6 && redis-server && brew services start rabbitmq && sudo rabbitmq-server -detached && celery -A jwxzs_2 worker -B -l info && python manage.py runserver





