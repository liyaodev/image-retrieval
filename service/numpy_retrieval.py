# -*- coding: utf-8 -*-

import os
import h5py
import numpy as np

THRESHOLD = float(os.environ.get('THRESHOLD', '0.85'))  # 检索阈值


class NumpyRetrieval(object):
    def __init__(self, index_dir, emb_size=512):
        self.emb_size = emb_size
        self.load(index_dir)

    def load(self, index_dir):
        h5f = h5py.File(index_dir, 'r')
        self.retrieval_db = h5f['dataset_1'][:]
        self.retrieval_name = h5f['dataset_2'][:]
        h5f.close()
        print("************* Done numpy indexing, Indexed {} documents *************".format(len(self.retrieval_db)))

    def retrieve(self, query_vector, search_size=3):
        distance_db = np.dot(query_vector, self.retrieval_db.T)
        optinal_dis = np.argsort(-distance_db.T)

        r_list = []
        for i in optinal_dis[:search_size]:
            name = self.retrieval_name[i]
            score = float(distance_db[i]) * 0.5 + 0.5
            if score > THRESHOLD:
                temp = {
                    "name": name,
                    "score": round(score, 6)
                }
                r_list.append(temp)
        
        return r_list
