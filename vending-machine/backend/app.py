from flask import Flask, request, jsonify
import time
import uuid
import random
from kubernetes import client, config

application = Flask(__name__)

options = ["rpslk"]

@application.route("/start-game", methods=['POST'])
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

    try:
        try:
            config.load_incluster_config()
        except config.ConfigException:
            try:
                config.load_kube_config()
            except config.ConfigException:
                raise Exception("Could not configure kubernetes python client")

        v1 = client.CoreV1Api() 
        
        namespace = "vending-machine"

        # convert minutes to seconds for Kubernetes
        lifetime_seconds = int(lifetime * 60)
        
        # generate a unique name
        pod_name = f"{game}-{uuid.uuid4().hex[:8]}"

        pod_spec = client.V1Pod(
            metadata=client.V1ObjectMeta(
                name=pod_name,
                labels={
                    "app": "rpslk-frontend",
                    "managed-by": "vm-backend"
                },
                ttl_seconds_after_finished=60
            ),
            spec=client.V1PodSpec(
                active_deadline_seconds=lifetime_seconds,
                restart_policy="Never",
                containers=[
                    client.V1Container(
                        name="rpslk-frontend",
                        image="rpslk-frontend:v1.0.0",
                        imagePullPolicy="Never",
                        ports=[client.V1ContainerPort(container_port=80)],
                        securityContext={
                            "readOnlyRootFilesystem": True,
                            "runAsNonRoot": True
                        }
                    )
                ]
            )
        )

        try:
            v1.create_namespaced_pod(namespace=namespace, body=pod_spec)
            print(f"Created pod {pod_name} with lifetime {lifetime}m")
        except client.exceptions.ApiException as e:
            raise Exception(f"Failed to create pod: {e}")

        print("Waiting for pod to get IP...")
        max_wait = 60 
        start_time = time.time()
        node_ips = []
        port = 0

        while True:
            if time.time() - start_time > max_wait:
                v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
                raise Exception("Could not create pod on time")

            try:
                pod_status = v1.read_namespaced_status(name=pod_name, namespace=namespace)
                
                if pod_status.status.phase == "Running" and pod_status.status.pod_ip:
                    node_ip = pod_status.status.host_ip

                    service_name = "rpslk-frontend"
                    
                    service = v1.read_namespaced_service(service_name, namespace)
                    port = service.spec.ports[0].node_port

                    break
                
                if pod_status.status.phase in ["Failed", "Succeeded"]:
                    raise Exception("Pod creation failed")

            except client.exceptions.ApiException:
                pass
            
            time.sleep(1)

        return jsonify({
            "pod": pod_name, 
            "status": "running", 
            "ip": f"{node_ip}:{port}", 
            "lifetime": lifetime
        })

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 400

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8000, debug=True)