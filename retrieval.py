# -*- coding: utf-8 -*-

import argparse
from service.vggnet import VGGNet
from service.numpy_retrieval import NumpyRetrieval
from service.faiss_retrieval import FaissRetrieval
from service.es_retrieval import ESRetrieval
from service.milvus_retrieval import MilvusRetrieval
import os
import sys
from os.path import dirname
BASE_DIR = dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)


class RetrievalEngine(object):

    def __init__(self, index_file, db_name):
        self.index_file = index_file
        self.db_name = db_name
        self.numpy_r = self.faiss_r = self.es_r = self.milvus_r = None

    def get_method(self, m_name):
        m_name = "%s_handler" % str(m_name)
        method = getattr(self, m_name, self.default_handler)
        return method

    def numpy_handler(self, query_vector, req_id=None):
        # numpy计算
        if self.numpy_r is None:
            self.numpy_r = NumpyRetrieval(self.index_file)
        return self.numpy_r.retrieve(query_vector)

    def faiss_handler(self, query_vector, req_id=None):
        # faiss计算
        if self.faiss_r is None:
            self.faiss_r = FaissRetrieval(self.index_file)
        return self.faiss_r.retrieve(query_vector)

    def es_handler(self, query_vector, req_id=None):
        # es计算
        if self.es_r is None:
            self.es_r = ESRetrieval(self.db_name, self.index_file)
        return self.es_r.retrieve(query_vector)

    def milvus_handler(self, query_vector, req_id=None):
        # milvus计算
        if self.milvus_r is None:
            self.milvus_r = MilvusRetrieval(self.db_name, self.index_file)
        return self.milvus_r.retrieve(query_vector)

    def default_handler(self, query_vector, req_id=None):
        return []


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_data", type=str, default=os.path.join(BASE_DIR, 'data', 'test', '001_accordion_image_0001.jpg'), help="test data path.")
    parser.add_argument("--index_file", type=str, default=os.path.join(BASE_DIR, 'index', 'train.h5'), help="index file path.")
    parser.add_argument("--db_name", type=str, default='image_retrieval', help="database name.")
    parser.add_argument("--engine", type=str, default='numpy', help="retrieval engine.")
    args = vars(parser.parse_args())
    # 1.图片推理
    model = VGGNet()
    query_vector = model.vgg_extract_feat(args["test_data"])
    # 2.图片检索
    re = RetrievalEngine(args["index_file"], args["db_name"])
    result = re.get_method(args["engine"])(query_vector, None)
    print(result)

