from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils import check_X_y, check_array
import scipy as sp
import numpy as np

class skTiMBL(BaseEstimator, ClassifierMixin):
    def __init__(self, prefix='timbl', algorithm=0, dist_metric=None,
                 k=1,  normalize=False, debug=0):
        self.prefix = prefix
        self.algorithm = algorithm
        self.dist_metric = dist_metric
        self.k = k
        self.normalize = normalize
        self.debug = debug

        self.classifier = TimblCl(self.prefix, "-a {} -k {}".format(self.algorithm, self.k),
                                            debug=True, flushthreshold=20000)

    def fit(self, X, y=None):
        X, y = check_X_y(X, y, dtype=np.int64, accept_sparse='csr')

        n_rows = X.shape[0]
        if sp.sparse.issparse(X):
            if self.debug: print('Features are sparse, choosing faster learning')

            self.classifier = TimblCl(self.prefix, "-a {} -k {} -N {}".format(self.algorithm,self.k, X.shape[1]),
                                              format='Sparse', debug=True, flushthreshold=20000)

            for i in range(n_rows):
                sparse = ['({},{})'.format(i+1, c) for i,c in zip(X[i].indices, X[i].data)]
                self.classifier.append(sparse,str(y[i]))

        else:
            if y.dtype != 'O':
                y = y.astype(str)

            for i in range(n_rows):
                self.classifier.append(list(X[i].toarray()[0]), y[i])

        self.classifier.train()
        return self


    def predict(self, X, y=None):
        X = check_array(X, dtype=np.int64, accept_sparse='csr')

        n_samples = X.shape[0]
        pred = []

        if sp.sparse.issparse(X):
            if self.debug: print('Features are sparse, choosing faster predictions')

            for i in range(n_samples):
                sparse = ['({},{})'.format(i+1, c) for i,c in zip(X[i].indices, X[i].data)]
                y_pred,_, distance = self.classifier.classify(sparse)
                pred.append(np.int64(y_pred))

        else:
            for i in range(n_samples):
                y_pred,_, distance = self.classifier.classify(list(X[i].toarray()[0]))
                pred.append(np.int64(y_pred))

        return pred


    def predict_proba(self, X, y=None):
        X = check_array(X, dtype=np.float64, accept_sparse='csr')

        n_samples = X.shape[0]

        pred = []

        if sp.sparse.issparse(X):
            print('Features are sparse, choosing faster predictions')

            for i in range(n_samples):
                sparse = ['({},{})'.format(i+1, c) for i,c in zip(X[i].indices, X[i].data)]
                _,dist, distance = self.classifier.classify(sparse)
                pred.append(np.int64(dist))

        else:
            for i in range(n_samples):
                _,proba, distance = self.classifier.classify(list(X[i].toarray()[0]))
                pred.append(np.float(proba))

        return pred

    def remove_flushfile(self):
        self.classifier.remove_flush()
