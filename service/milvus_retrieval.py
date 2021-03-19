# -*- coding: utf-8 -*-

import os
import h5py
import numpy as np
from pprint import pprint
from milvus import Milvus, IndexType, MetricType

THRESHOLD = float(os.environ.get('THRESHOLD', '0.85'))  # 检索阈值

class MilvusRetrieval(object):
    def __init__(self, index_name, index_dir,
        host=os.environ.get("MILVUS_HOST", "127.0.0.1"),
        port=os.environ.get("MILVUS_PORT", 19530)):
        self.client = Milvus(host, port)
        self.index_name = index_name
        self.load(index_dir)

    def load(self, index_dir):
        # 1. 读取索引
        h5f = h5py.File(index_dir, 'r')
        self.retrieval_db = h5f['dataset_1'][:]
        self.retrieval_name = h5f['dataset_2'][:]
        h5f.close()
        # 2. 入库Milvus
        if self.index_name in self.client.list_collections()[1]:
            self.client.drop_collection(collection_name=self.index_name)
        self.client.create_collection({'collection_name': self.index_name, 'dimension': 512, 'index_file_size': 1024, 'metric_type': MetricType.IP})
        self.id_dict = {}
        status, ids = self.client.insert(collection_name=self.index_name, records=[i.tolist() for i in self.retrieval_db])
        for i, val in enumerate(self.retrieval_name):
            self.id_dict[ids[i]] = str(val)
        self.client.create_index(self.index_name, IndexType.FLAT, {'nlist': 16384})
        # pprint(self.client.get_collection_info(self.index_name))
        print("************* Done milvus indexing, Indexed {} documents *************".format(len(self.retrieval_db)))

    def retrieve(self, query_vector, search_size=3):
        r_list = []
        _, vectors = self.client.search(collection_name=self.index_name, query_records=[query_vector], top_k=search_size, params={'nprobe': 16})
        for v in vectors[0]:
            score = float(v.distance) * 0.5 + 0.5
            if score > THRESHOLD:
                temp = {
                    "id": v.id,
                    "name": self.id_dict[v.id],
                    "score": round(score, 6)
                }
                r_list.append(temp)

        return r_list
