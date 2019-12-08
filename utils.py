from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils import check_X_y, check_array
from timbl import TimblClassifier
import scipy as sp
import numpy as np

class skTiMBL(BaseEstimator, ClassifierMixin):
    def __init__(self, prefix='timbl', algorithm=4, dist_metric=None,
                 k=1,  normalize=False, debug=0, flushdir=None):
        self.prefix = prefix
        self.algorithm = algorithm
        self.dist_metric = dist_metric
        self.k = k
        self.normalize = normalize
        self.debug = debug
        self.flushdir = flushdir


    def _make_timbl_options(self, *options):
        """
        -a algorithm
        -m metric
        -w weighting
        -k amount of neighbours
        -d class voting weights
        -L frequency threshold
        -T which feature index is label
        -N max number of features
        -H turn hashing on/off

        This function still has to be made, for now the appropriate arguments
        can be passed in fit()
        """
        pass


    def fit(self, X, y):
        X, y = check_X_y(X, y, dtype=np.int64, accept_sparse='csr')

        n_rows = X.shape[0]
        self.classes_ = np.unique(y)

        if sp.sparse.issparse(X):
            if self.debug: print('Features are sparse, choosing faster learning')

            self.classifier = TimblClassifier(self.prefix, "-a{} -k{} -N{} -vf".format(self.algorithm,self.k, X.shape[1]),
                                              format='Sparse', debug=True, sklearn=True, flushdir=self.flushdir,
                                              flushthreshold=20000, normalize=self.normalize)

            for i in range(n_rows):
                sparse = ['({},{})'.format(i+1, c) for i,c in zip(X[i].indices, X[i].data)]
                self.classifier.append(sparse,str(y[i]))

        else:

            self.classifier = TimblClassifier(self.prefix, "-a{} -k{} -N{} -vf".format(self.algorithm, self.k, X.shape[1]),
                                              debug=True, sklearn=True, flushdir=self.flushdir, flushthreshold=20000,
                                              normalize=self.normalize)

            if y.dtype != 'O':
                y = y.astype(str)

            for i in range(n_rows):
                self.classifier.append(list(X[i].toarray()[0]), y[i])

        self.classifier.train()
        return self


    def _timbl_predictions(self, X, part_index, y=None):
        choices = {0 : lambda x : x.append(np.int64(label)),
                   1 : lambda x : x.append([np.float(distance)]),
                  }
        X = check_array(X, dtype=np.float64, accept_sparse='csr')

        n_samples = X.shape[0]

        pred = []
        func = choices[part_index]
        if sp.sparse.issparse(X):
            if self.debug: print('Features are sparse, choosing faster predictions')

            for i in range(n_samples):
                sparse = ['({},{})'.format(i+1, c) for i,c in zip(X[i].indices, X[i].data)]
                label,proba, distance = self.classifier.classify(sparse)
                func(pred)

        else:
            for i in range(n_samples):
                label,proba, distance = self.classifier.classify(list(X[i].toarray()[0]))
                func(pred)

        return np.array(pred)



    def predict(self, X, y=None):
        return self._timbl_predictions(X, part_index=0)


    def predict_proba(self, X, y=None):
        """
        TIMBL is a discrete classifier. It cannot give probability estimations.
        To ensure that scikit-learn functions with TIMBL (and especially metrics
        such as ROC_AUC), this method is implemented.

        For ROC_AUC, the classifier corresponds to a single point in ROC space,
        instead of a probabilistic continuum such as classifiers that can give
        a probability estimation (e.g. Linear classifiers). For an explanation,
        see Fawcett (2005).
        """
        return predict(X)


    def decision_function(self, X, y=None):
        """
        The decision function is interpreted here as being the distance between
        the instance that is being classified and the nearest point in k space.
        """
        return self._timbl_predictions(X, part_index=1)


