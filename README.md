## 图片向量检索服务构建

该系统使用VGG（图像特征提取模型）和Numpy、Faiss、ES、Milvus构建了图像搜索流程。 系统架构如下：

<img src="pic/system_arch.png" width = "250" height = "300" alt="system_arch" align=center />

## 构建环境

### Docker-Compose

```shell
# 启动
make up

# 开发运行
make dev

# 关闭
make down
```

### Docker 环境

详见[环境安装](./docs/build.md)

### 操作简介

操作一：构建基础索引

```shell
python index.py
--train_data：自定义训练图片文件夹路径，默认为`<ROOT_DIR>/data/train`
--index_file：自定义索引文件存储路径，默认为`<ROOT_DIR>/index/train.h5`

# 示例：
python index.py --train_data /www/server/data/train --index_file /www/server/index/train.h5
```

操作二：使用相似检索

```shell
python retrieval.py --engine=numpy
--test_data：自定义测试图片详细地址，默认为`<ROOT_DIR>/data/test/001_accordion_image_0001.jpg`
--index_file：自定义索引文件存储路径，默认为`<ROOT_DIR>/index/train.h5`
--db_name：自定义ES或者Milvus索引库名，默认为`image_retrieval`
--engine：自定义检索引擎类型，默认为`numpy`，可选包括：numpy、faiss、es、milvus

# 示例：
python retrieval.py --engine=numpy --index_file /www/server/index/train.h5 --test_data /www/server/data/test/001_accordion_image_0001.jpg

python retrieval.py --engine=faiss --index_file /www/server/index/train.h5 --test_data /www/server/data/test/001_accordion_image_0001.jpg

python retrieval.py --engine=es --index_file /www/server/index/train.h5 --test_data /www/server/data/test/001_accordion_image_0001.jpg

python retrieval.py --engine=milvus --index_file /www/server/index/train.h5 --test_data /www/server/data/test/001_accordion_image_0001.jpg
```

### 附录

参考1：https://github.com/willard-yuan/flask-keras-cnn-image-retrieval <br>
参考2：https://github.com/zilliz-bootcamp/image_search
