from kubernetes import config, client

from gin_parser import GinParser
from get_logs import stream_pods_in_namespace, read_namespace_logs
from submit_job import create_pod_object, create_namespace_and_pods


def parse_and_submit(api, gin_file, container_name, namespace_name, pod_name='pod', reset_namespace=True, **kwargs):
    """
    Parse the gin-config file, make pods from container_name in namespace_name, and run the pods on the k8s cluster.
    :param api: client.CoreV1Api object
    :param gin_file: path to the gin-config file
    :param container_name: container to pull to make the pod
    :param namespace_name: namespace to execute the pods in
    :param pod_name: this doesn't really matter except for aesthetics. the name that will show up in the list of pods
    :param reset_namespace: if true, delete the namespace before creating new pods
    :param resources: a dict, containing request and limit for resources for the pod in the following format {'requests': {"cpu": "100m", "memory": "200Mi"}, 'limits': {"cpu": "100m", "memory": "200Mi"}}
    :param env: a dict of name-value pairs of environment variables to be passed to the pod
    :return: None
    """
    with open(gin_file) as f:
        pods = [create_pod_object(pod_name, container_name, i, conf, **kwargs) for i, conf in enumerate(GinParser(f))]
        create_namespace_and_pods(api, namespace_name, pods, reset_namespace=reset_namespace)


if __name__ == '__main__':
    config.load_kube_config()
    v1 = client.CoreV1Api()

    parse_and_submit(v1, 'test.gin', 'localhost:5001/git_pod', 'custom-space', 'git-pod', env={'GIT_REPO_URL':'https://github.com/pranavgade20/grok/', 'PY_ENTRYPOINT': 'scripts/train.py', 'TERM': 'linux'})
    stream_pods_in_namespace(v1, 'custom-space')
