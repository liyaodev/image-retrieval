# -*- coding: utf-8 -*-

import os
import h5py
import numpy as np
import faiss

THRESHOLD = float(os.environ.get('THRESHOLD', '0.85'))  # 检索阈值


class FaissRetrieval(object):
    def __init__(self, index_dir, emb_size=512):
        self.emb_size = emb_size
        self.load(index_dir)

    def load(self, index_dir):
        # 1.读取索引
        h5f = h5py.File(index_dir, 'r')
        self.retrieval_db = h5f['dataset_1'][:]
        self.retrieval_name = h5f['dataset_2'][:]
        h5f.close()
        # 2. 加载faiss
        self.retrieval_db = np.asarray(self.retrieval_db).astype(np.float32)
        self.index = faiss.IndexFlatIP(self.emb_size)
        # self.index.train(self.retrieval_db)
        self.index.add(self.retrieval_db)
        print("************* Done faiss indexing, Indexed {} documents *************".format(len(self.retrieval_db)))

    def retrieve(self, query_vector, search_size=3):
        score_list, index_list = self.index.search(np.array([query_vector]).astype(np.float32), search_size)
        r_list = []
        for i, val in enumerate(index_list[0]):
            name = self.retrieval_name[int(val)]
            score = float(score_list[0][i]) * 0.5 + 0.5
            if score > THRESHOLD:
                temp = {
                    "name": name,
                    "score": round(score, 6)
                }
                r_list.append(temp)
        
        return r_list
