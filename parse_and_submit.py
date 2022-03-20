from kubernetes import config, client

from gin_parser import GinParser
from stream_stdout import stream_pods_in_namespace
from submit_job import create_pod_object, create_namespace_and_pods


def parse_and_submit(api, gin_file, container_name, namespace_name, pod_name='pod', reset_namespace=True):

    with open(gin_file) as f:
        pods = [create_pod_object(pod_name, container_name, i, conf) for i, conf in enumerate(GinParser(f))]
        create_namespace_and_pods(api, namespace_name, pods, reset_namespace=reset_namespace)


if __name__ == '__main__':
    config.load_kube_config()
    v1 = client.CoreV1Api()

    parse_and_submit(v1, 'test.gin', 'localhost:5001/echopod', 'custom-space', 'echopod')
    stream_pods_in_namespace(v1, 'custom-space')
