# ghsok
gin hyperparameter search on kubernetes(ghsok) allows you to run containers on kubernetes clusters with parameters from a gin config.

Every list in the gin config is treated as something you want to search over, and differnet k8s pods are launched for each cartesian product of the list contents.

The resulting gin config is passes as the environment variable 'GIN_CONFIG' to the pod
