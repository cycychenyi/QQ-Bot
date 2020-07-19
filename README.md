## QQ Bot

#### 常用命令

- 进入 Python 虚拟环境。

```bash
. venv/bin/activate
```

- 生成 Python 虚拟环境的第三方依赖需求。

```bash
pip-chill --no-version > requirements.txt
```

- 后台运行 Python 脚本。

```bash
nohup python3 bot.py >> output.log 2>&1 &
```

- 查看后台运行的 bot.py 进程。

```bash
ps -aux | grep bot.py
```

- 查看后台运行的 docker 容器。

```bash
docker ps
```

- 复现 docker 运行命令。

```bash
runlike <容器名> -p
```