from time import sleep
from typing import Union, Any

from kubernetes import client, config


def gin_config_from_dict(params: dict):
    return '\n'.join(str(x)+"="+str(y) for x, y in params.items())


def create_pod_object(name:str, container: str, index: int, params: Union[dict, str, Any]):
    container = client.V1Container(
        name=f"{name}-container",
        image=container,
        resources=client.V1ResourceRequirements(
            requests={"cpu": "100m", "memory": "200Mi"},
            limits={"cpu": "500m", "memory": "500Mi"},
        ),
        env=[client.V1EnvVar(name="GIN_CONFIG", value=gin_config_from_dict(params) if isinstance(params, dict) else str(params))]
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

    print("\n[INFO] pod created.\n")
    print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
    print(
        "%s\t\t%s\t%s\t\t%s\n"
        % (
            resp.metadata.namespace,
            resp.metadata.name,
            resp.metadata.generation,
            resp.spec.containers[0].image,
        )
    )

    return resp


def create_namespace_and_pods(api, namespace: str, pods: list):
    resp = api.list_namespace()
    if any(namespace == x.metadata.name for x in resp.items):
        try:
            print(f"[WARN] deleting namespace `{namespace}` with same name")
            api.delete_namespace(name=namespace)
            while any(namespace == x.metadata.name for x in api.list_namespace().items):
                # waiting for namespace to die
                sleep(1)
        except client.ApiException:
            print("[WARN] can't delete namespace, it was probably deleted elsewhere")
    resp = api.create_namespace(
        body=client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace))
    )

    for pod in pods:
        create_or_replace_pod(api, pod, namespace)


def main():
    config.load_kube_config()
    v1 = client.CoreV1Api()

    pod = create_pod_object('echopod', 'localhost:5001/echopod', 0, {'a': 123, 'b': 'asdf'})
    create_namespace_and_pods(v1, "my-custom-namespace", [pod])


if __name__ == "__main__":
    main()
