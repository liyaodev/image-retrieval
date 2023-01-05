
## 手动构建环境

### 基础环境安装

Python版本：3.8.12

```shell
pip install -r requirements.txt
```

### ES服务端安装

```shell
docker run -it -d -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.5.0
```

### Milvus服务端安装

安装指南：https://milvus.io/cn/docs/v1.1.1/milvus_docker-cpu.md <br>
下载配置

```shell
mkdir -p milvus/conf && cd milvus/conf
wget https://raw.githubusercontent.com/milvus-io/milvus/v1.1.1/core/conf/demo/server_config.yaml
```

服务启动

```shell
docker run -d --name milvus_cpu_1.1.1 \
-p 19530:19530 \
-p 19121:19121 \
-v <ROOT_DIR>/milvus/db:/var/lib/milvus/db \
-v <ROOT_DIR>/milvus/conf:/var/lib/milvus/conf \
-v <ROOT_DIR>/milvus/logs:/var/lib/milvus/logs \
-v <ROOT_DIR>/milvus/wal:/var/lib/milvus/wal \
milvusdb/milvus:1.1.1-cpu-d061621-330cc6
```
