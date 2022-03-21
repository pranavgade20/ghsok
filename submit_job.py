import threading
from time import sleep
from typing import Union, Any

from kubernetes import client, config


def gin_config_from_dict(params: dict):
    return '\n'.join(str(x)+"="+str(y) for x, y in params.items())


def create_pod_object(name: str, container: str, index: int, params: Union[dict, str, Any], **kwargs):
    container = client.V1Container(
        name=f"{name}-container",
        image=container,
        resources=client.V1ResourceRequirements(
            requests=kwargs['resources']['requests'] if 'resources' in kwargs and 'requests' in kwargs['resources'] else {"cpu": "100m", "memory": "200Mi"},
            limits=kwargs['resources']['limits'] if 'resources' in kwargs and 'limits' in kwargs['resources'] else {"cpu": "100m", "memory": "200Mi"},
        ),
        env=[client.V1EnvVar(name="GIN_CONFIG", value=gin_config_from_dict(params) if isinstance(params, dict) else str(params)), *([client.V1EnvVar(name=k, value=v) for k, v in kwargs['env']] if 'env' in kwargs else [])]
    )

    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(name=f"{name}-{index}"),
        spec=client.V1PodSpec(containers=[container], restart_policy="Never"),
    )

    return pod


def create_or_replace_pod(api, deployment, namespace):
    resp = api.list_namespaced_pod(namespace=namespace)
    if any(deployment.metadata.name == x.metadata.name for x in resp.items):
        try:
            print("[WARN] deleting pod with same name")
            api.delete_namespaced_pod(
                name=deployment.metadata.name, namespace=namespace
            )
            while any(deployment.metadata.name == x.metadata.name for x in api.list_namespaced_pod(namespace="default").items):
                # waiting for pod to die
                sleep(1)
        except client.ApiException:
            print("[WARN] can't delete pod, it probably exited")
    resp = api.create_namespaced_pod(
        body=deployment, namespace=namespace
    )

    print(f"[INFO] {resp.metadata.name}(from {resp.spec.containers[0].image}) created in {resp.metadata.namespace}")

    return resp


def create_namespace_and_pods(api, namespace: str, pods: list, reset_namespace=True):
    if reset_namespace:
        resp = api.list_namespace()
        if any(namespace == x.metadata.name for x in resp.items):
            try:
                print(f"[WARN] deleting namespace `{namespace}` with same name")
                api.delete_namespace(name=namespace)
                while any(namespace == x.metadata.name for x in api.list_namespace().items):
                    # waiting for namespace to die
                    sleep(1)
            except client.ApiException:
                print("[WARN] can't delete namespace, it was probably deleted already")
    resp = api.create_namespace(
        body=client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace))
    )

    threads = [threading.Thread(target=create_or_replace_pod, args=(api, pod, namespace)) for pod in pods]
    any(t.start() for t in threads)
    any(t.join() for t in threads)


def main():
    config.load_kube_config()
    v1 = client.CoreV1Api()

    pod = create_pod_object('echopod', 'localhost:5001/echopod', 0, {'a': 123, 'b': 'asdf'})
    create_namespace_and_pods(v1, "my-custom-namespace", [pod])


if __name__ == "__main__":
    main()
