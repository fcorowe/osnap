from warnings import warn

import numpy as np
from hdbscan import HDBSCAN
from region.max_p_regions.heuristics import MaxPRegionsHeu
from region.p_regions.azp import AZP
from region.skater.skater import Spanning_Forest
from sklearn.cluster import (AffinityPropagation, AgglomerativeClustering,
                             KMeans, SpectralClustering)
from sklearn.mixture import GaussianMixture
from spenc import SPENC

# Sklearn a-spatial models


def ward(X, n_clusters=5, **kwargs):
    """Agglomerative clustering using Ward linkage


    Parameters
    ----------
    X  : array-like
        n x k attribute data

    n_clusters : int, optional, default: 8
        The number of clusters to form.


    Returns
    -------

    model: sklearn AgglomerativeClustering instance

    """

    model = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
    model.fit(X)
    return model


def kmeans(X, n_clusters=5, seed=None, **kwargs):
    """K-Means clustering


    Parameters
    ----------

    X  : array-like
         n x k attribute data

    n_clusters : int, optional, default: 8
        The number of clusters to form as well as the number of centroids to
        generate.

    seed: int, optional, default: None
        The seed to set the random number generator. If none, no seed is used
        and the random number generator will be the RandomState instance used
        by np.random.


    Returns
    -------

    model: sklearn KMeans instance

    """

    model = KMeans(n_clusters, random_state=seed)
    model.fit(X)
    return model


def affinity_propagation(X, damping=0.8, preference=-1000, verbose=False,
                         max_iter=500, **kwargs):
    """Clustering with Affinity Propagation


    Parameters
    ----------

    X  : array-like
         n x k attribute data

    preference :  array-like, shape (n_samples,) or float, optional,
                  default: None
        The preference parameter passed to scikit-learn's affinity propagation
        algorithm

    damping: float, optional, default: 0.8
        The damping parameter passed to scikit-learn's affinity propagation
        algorithm

    max_iter : int, optional, default: 1000
        Maximum number of iterations


    Returns
    -------

    model: sklearn AffinityPropagation instance

    """
    model = AffinityPropagation(preference=preference, damping=damping,
                                verbose=verbose)
    model.fit(X)
    return model


def spectral(X, n_clusters=5, n_jobs=-1, affinity='rbf', **kwargs):
    """A-spatial Spectral Clustering


    Parameters
    ----------

    X  : array-like
         n x k attribute data

    n_clusters : int, optional, default: 8
        The number of clusters to form as well as the number of centroids to
        generate.

    n_jobs: int, optional, default: -1
        The damping parameter passed to scikit-learn's affinity propagation
        algorithm

    affinity : str, optional, default 'rbf'
        The kernel type passed to scikit-learn's SpectralClustering algorithm

    Returns
    -------

    model: sklearn SpectralClustering instance

    """

    model = SpectralClustering(n_clusters=n_clusters, n_jobs=n_jobs,
                               affinity=affinity)
    model.fit(X)
    return model


def gaussian_mixture(X, n_clusters=5, covariance_type="full", best_model=False,
                     max_clusters=10, random_state=None, **kwargs):
    """Clustering with Gaussian Mixture Model


    Parameters
    ----------

    X  : array-like
        n x k attribute data

    n_clusters : int, optional, default: 5
        The number of clusters to form.

    covariance_type: str, optional, default: "full""
        The covariance parameter passed to scikit-learn's GaussianMixture
        algorithm

    best_model: bool, optional, default: False
        Option for finding endogenous K according to Bayesian Information
        Criterion

    max_clusters: int, optional, default:10
        The max number of clusters to test if using `best_model` option

    random_state: int, optional, default: None
        The seed used to generate replicable results

    Returns
    -------

    model: sklearn GaussianMixture instance

    """
    if random_state is None:
        warn("Note: Gaussian Mixture Clustering is probabilistic--\
cluster labels may be different for different runs. If you need consistency,\
you should set the `random_state` parameter")

    if best_model is True:

        # selection routine from
        # https://plot.ly/scikit-learn/plot-gmm-selection/
        lowest_bic = np.infty
        bic = []
        max = max_clusters + 1
        n_components_range = range(1, max)
        cv_types = ['spherical', 'tied', 'diag', 'full']
        for cv_type in cv_types:
            for n_components in n_components_range:
                # Fit a Gaussian mixture with EM
                gmm = GaussianMixture(n_components=n_components,
                                      random_state=random_state,
                                      covariance_type=cv_type)
                gmm.fit(X)
                bic.append(gmm.bic(X))
                if bic[-1] < lowest_bic:
                    lowest_bic = bic[-1]
                    best_gmm = gmm

        bic = np.array(bic)
        model = best_gmm

    else:
        model = GaussianMixture(n_components=n_clusters,
                                random_state=random_state,
                                covariance_type=covariance_type)
    model.fit(X)
    model.labels_ = model.predict(X)
    return model


def hdbscan(X, min_cluster_size=5, gen_min_span_tree=True, **kwargs):
    """Clustering with Hierarchical DBSCAN

    Parameters
    ----------
    X : array-like
         n x k attribute data

    min_cluster_size : int, default: 5
        the minimum number of points necessary to generate a cluster

    gen_min_span_tree : bool
        Description of parameter `gen_min_span_tree` (the default is True).

    Returns
    -------
    model: hdbscan HDBSCAN instance

    """

    model = HDBSCAN(min_cluster_size=min_cluster_size)
    model.fit(X)
    return model

# Spatially Explicit/Encouraged Methods


def ward_spatial(X, w, n_clusters=5, **kwargs):
    """Agglomerative clustering using Ward linkage with a spatial connectivity
       constraint

    Parameters
    ----------
    X : array-like
         n x k attribute data

    w : PySAL W instance
        spatial weights matrix

    n_clusters : int, optional, default: 5
        The number of clusters to form.


    Returns
    -------
    model: sklearn AgglomerativeClustering instance

    """

    model = AgglomerativeClustering(n_clusters=n_clusters,
                                    connectivity=w.sparse,
                                    linkage='ward')
    model.fit(X)
    return model


def spenc(X, w, n_clusters=5, gamma=1, **kwargs):
    """Spatially encouraged spectral clustering

    :cite:`wolf2018`

    Parameters
    ----------
    X : array-like
         n x k attribute data

    w : PySAL W instance
        spatial weights matrix

    n_clusters : int, optional, default: 5
        The number of clusters to form.

    gamma : int, default:1
        TODO.


    Returns
    -------
    model: spenc SPENC instance

    """
    model = SPENC(n_clusters=n_clusters,
                  gamma=gamma)

    model.fit(X, w.sparse)
    return model


def skater(X, w, n_clusters=5, floor=-np.inf, trace=False,
           islands='increase', **kwargs):
    """SKATER spatial clustering algorithm.

    Parameters
    ----------
    X : array-like
         n x k attribute data

    w : PySAL W instance
        spatial weights matrix

    n_clusters : int, optional, default: 5
        The number of clusters to form.

    floor : type
        TODO.

    trace : type
        TODO.

    islands : type
        TODO.


    Returns
    -------

    model: skater SKATER instance

    """

    model = Spanning_Forest()
    model.fit(n_clusters, w, data=X, quorum=floor, trace=trace)
    model.labels_ = model.current_labels_
    return model


def azp(X, w, n_clusters=5, **kwargs):
    """AZP clustering algorithm

    Parameters
    ----------
    X : array-like
         n x k attribute data

    w : PySAL W instance
        spatial weights matrix

    n_clusters : int, optional, default: 5
        The number of clusters to form.


    Returns
    -------
    model: region AZP instance

    """

    model = AZP()
    model.fit_from_w(attr=X, w=w, n_regions=n_clusters)
    return model


def max_p(X, w, threshold_variable="count", threshold=10, **kwargs):
    """Max-p clustering algorithm
    :cite:`Duque2012`

    Parameters
    ----------
    X : array-like
         n x k attribute data

    w : PySAL W instance
        spatial weights matrix

    threshold_variable : str, default:"count"
        attribute variable to use as floor when calculate

    threshold : int, default:10
        integer that defines the upper limit of a variable that can be grouped
        into a single region


    Returns
    -------
    model: region MaxPRegionsHeu instance

    """
    model = MaxPRegionsHeu()
    model.fit_from_w(w, X.values, threshold_variable, threshold)
    return model
