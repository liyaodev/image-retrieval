# -*- coding: utf-8 -*-

import os
import h5py
import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

THRESHOLD = float(os.environ.get('THRESHOLD', '0.85'))  # 检索阈值
INDEX_TABLE = {
    "settings": {
        "number_of_shards": 2,
        "number_of_replicas": 1
    },
    "mappings": {
        "dynamic": "true",
        "_source": {
            "enabled": "true"
        },
        "properties": {
            "image_vector": {
                "type": "dense_vector",
                "dims": 512
            },
            "id": {
                "type": "keyword"
            },
            "name": {
                "type": "keyword"
            }
        }
    }
}


class ESRetrieval(object):
    def __init__(self, index_name, index_dir,
        host=os.environ.get("ES_HOST", "127.0.0.1"),
        port=os.environ.get("ES_PORT", 9200)):
        self.index_name = index_name
        self.client = Elasticsearch([host])
        self.load(index_dir)

    def load(self, index_dir):
        def index_batch(docs):
            requests = []
            for i, doc in enumerate(docs):
                request = doc
                request["_op_type"] = "index"
                request["_index"] = self.index_name
                requests.append(request)
            bulk(self.client, requests)
        # 1. 读取索引
        h5f = h5py.File(index_dir, 'r')
        self.retrieval_db = h5f['dataset_1'][:]
        self.retrieval_name = h5f['dataset_2'][:]
        h5f.close()
        # 2. 入库ES
        r_list = []
        for i, val in enumerate(self.retrieval_name):
            temp = {
                'id': i,
                'name': str(val),
                'image_vector': self.retrieval_db[i].tolist()
            }
            r_list.append(temp)
        self.client.indices.delete(index=self.index_name, ignore=[404])
        self.client.indices.create(index=self.index_name, body=INDEX_TABLE)
        docs = []
        count = 0
        batch_size = 1000
        for doc in r_list:
            docs.append(doc)
            count += 1
            if count % batch_size == 0:
                index_batch(docs)
                docs = []
        if docs:
            index_batch(docs)
        self.client.indices.refresh(index=self.index_name)
        print("************* Done es indexing, Indexed {} documents *************".format(len(self.retrieval_db)))

    def retrieve(self, query_vector, search_size=3):

        # script_query = {
        #     "script_score": {
        #         "query": {"match_all": {}},
        #         "script": {
        #             "source": "cosineSimilarity(params.query_vector, doc['image_vector']) + 1.0",
        #             "params": {"query_vector": query_vector}
        #         }
        #     }
        # }

        # script_query = {
        #     "script_score": {
        #         "query": {"match_all": {}},
        #         "script": {
        #             "source": """
        #                 double value = dotProduct(params.query_vector, doc['image_vector']);
        #                 return sigmoid(1, Math.E, -value); 
        #                 """,
        #             "params": {"query_vector": query_vector}
        #         }
        #     }
        # }

        # script_query = {
        #     "script_score": {
        #         "query": {"match_all": {}},
        #         "script": {
        #             "source": "1 / (1 + l1norm(params.queryVector, doc['image_vector']))",
        #             "params": {
        #             "queryVector": query_vector
        #             }
        #         }
        #     }
        # }

        # script_query = {
        #     "script_score": {
        #         "query": {"match_all": {}},
        #         "script": {
        #             "source": "1 / (1 + l2norm(params.queryVector, doc['image_vector']))",
        #             "params": {
        #             "queryVector": query_vector
        #             }
        #         }
        #     }
        # }

        script_query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": """
                        double value = doc['image_vector'].size() == 0 ? 0 : dotProduct(params.query_vector, doc['image_vector']);
                        return value;
                        """,
                    "params": {"query_vector": query_vector}
                }
            }
        }
        response = self.client.search(
            index=self.index_name,
            body={
                "size": search_size,
                "query": script_query,
                "_source": {"includes": ["id", "name", "face_vector"]}
            }
        )
        r_list = []
        for hit in response["hits"]["hits"]:
            score = float(hit['_score']) * 0.5 + 0.5
            name = hit['_source']["name"]
            if name.encode("utf-8") and score > THRESHOLD:
                temp = {
                    "id": hit['_source']["id"],
                    "name": name,
                    "score": round(score, 6)
                }
                r_list.append(temp)
        
        return r_list
