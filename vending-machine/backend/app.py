from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

options = ["rpslk"]
logging.basicConfig(filename='./exception-log.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

@app.route("/start-game", methods=['POST'])
def start_game():
    content = request.get_json(silent=True)
    if not content:
        return jsonify({"error": "Missing or invalid JSON"}), 400

    game = content.get("game")
    lifetime = content.get("lifetime")
    if not game or not lifetime:
        return jsonify({"error": "Missing or invalid JSON"}), 400

    game = str(game).lower()
    if game not in options:
        return jsonify({"error": "Missing or invalid JSON"}), 400

    #after request data validation, the program begins

    try:
        from kubernetes import client, config
        import time
        import random

        DEPLOYMENT_NAME = "rpslk-frontend"
        WAITING_TIMEOUT = 20

        config.load_config()
        #config.load_kube_config()

        api = client.AppsV1Api()
        core_api = client.CoreV1Api()

        deployment_obj = api.read_namespaced_deployment_scale(
            name=DEPLOYMENT_NAME,
            namespace="default"
        )
        
        current_replicas = int(deployment_obj.status.replicas)
        desired_replicas = current_replicas + 1        

        if desired_replicas > 10:
            return jsonify({"warning": "too many concurrent games, pod creation not possible"}), 400

        patch_body = {
            "spec": {
                "replicas": desired_replicas
            }
        }

        api.patch_namespaced_deployment_scale(
            name=DEPLOYMENT_NAME,
            namespace="default",
            body=patch_body
        )

        current_status = api.read_namespaced_deployment(DEPLOYMENT_NAME, "default").status

        slept_time = 0.0

        while desired_replicas != current_status.ready_replicas:
            print("waiting 0.5s for available pod, total time waited: ", slept_time)
            #print("current status: ", current_status)
            time.sleep(0.5)
            slept_time += 0.5

            if slept_time > WAITING_TIMEOUT:
                raise Exception("replica wasnt created on time")

            current_status = api.read_namespaced_deployment(DEPLOYMENT_NAME, "default").status

        #get a list of all cluster nodes IPs
        nodes = core_api.list_node().items
        node_ips = []

        for node in nodes:
            for address in node.status.addresses:
                if address.type == "InternalIP":
                    node_ips.append(address.address)

        #get the service port
        service = core_api.read_namespaced_service(DEPLOYMENT_NAME, "default")
        port = service.spec.ports[0].node_port

        pods = core_api.list_namespaced_pod(
            namespace="default",
            label_selector="app=rpslk-frontend"
        )
        
        pod_name = pods.items[desired_replicas - 1].metadata.name #assumes last pod is the newly created

        return jsonify({"pod": pod_name, "status": "running", "ip": f"{random.choice(node_ips)}:{port}", "lifetime": lifetime})
    except Exception as e:
        logger.error(e)
        return jsonify({"error": "Internal error"}), 400

    return jsonify({"error": "Internal error"}), 400

