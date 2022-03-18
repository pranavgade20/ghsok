from kubernetes import config, client

from gin_parser import GinParser
from submit_job import create_pod_object, create_namespace_and_pods


def parse_and_submit(gin_file, container_name, namespace_name, pod_name='pod'):
    config.load_kube_config()
    v1 = client.CoreV1Api()

    with open(gin_file) as f:
        pods = [create_pod_object(pod_name, container_name, i, conf) for i, conf in enumerate(GinParser(f))]
        create_namespace_and_pods(v1, namespace_name, pods)

if __name__ == '__main__':
    parse_and_submit('test.gin', 'localhost:5001/echopod', 'custom-space', 'echopod')
