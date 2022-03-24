import curses
import threading
from time import sleep

from kubernetes import client
from kubernetes.watch import Watch


def stream_pods_in_namespace(api: client.CoreV1Api, namespace: str):
    pods = [x.metadata.name for x in api.list_namespaced_pod(namespace=namespace).items]
    latest_logs = ["" for _ in pods]

    def stream_pod_logs(api: client.CoreV1Api, pod: str, namespace: str, logs_list: [str], index: int):
        phase = 'Pending'
        while phase != 'Succeeded' and phase != 'Failed':
            while phase != 'Running':
                phase = api.read_namespaced_pod_status(name=pod, namespace=namespace).status.phase
                logs_list[index] = phase
                sleep(1)
            w = Watch()
            try:
                # with open(f'logs/{pod}.log', 'w') as pod_file:
                for e in w.stream(api.read_namespaced_pod_log, name=pod, namespace=namespace):
                    logs_list[index] = e
                    # pod_file.write(e + '\n')
            except client.ApiException as ex:
                phase = 'Succeeded or Crashed'
            phase = api.read_namespaced_pod_status(name=pod, namespace=namespace).status.phase

    threads = [threading.Thread(target=stream_pod_logs, args=(api, pod, namespace, latest_logs, i), daemon=True) for
               i, pod in enumerate(pods)]
    any(t.start() for t in threads)

    def print_logs_in_curses(stdscr):
        stdscr.nodelay(1)  # 0.1 second

        inp = -1
        while any(t.is_alive() for t in threads):
            stdscr.erase()
            if inp == -1:
                stdscr.addstr(0, 0, "Press e to exit")
            elif inp == ord('e'):
                break
            else:
                stdscr.addstr(0, 0, "unknown command")

            for i, log in enumerate(latest_logs):
                stdscr.addstr(i + 1, 0, pods[i] + ' | ' + log[log.rfind("\r")+1:])  # carriage returns mess up the output
            stdscr.refresh()
            inp = stdscr.getch()

    curses.wrapper(print_logs_in_curses)


def read_namespaced_pod_logs(api: client.CoreV1Api, pod: str, namespace: str) -> str:
    ret = []
    try:
        w = Watch()
        for e in w.stream(api.read_namespaced_pod_log, name=pod, namespace=namespace):
            ret.append(e)
    except client.ApiException:
        ret.append(api.read_namespaced_pod_status(name=pod, namespace=namespace).status.phase)

    return '\n'.join(ret)


def read_namespace_logs(api: client.CoreV1Api, namespace: str) -> dict[str, str]:
    pods = [x.metadata.name for x in api.list_namespaced_pod(namespace=namespace).items]
    return {pod: read_namespaced_pod_logs(api, pod, namespace) for pod in pods}
