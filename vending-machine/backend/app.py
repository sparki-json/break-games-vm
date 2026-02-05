from flask import Flask, request, jsonify

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

    #after request data validation, the program begins

    try:
        from kubernetes import client, config
        import time
        import uuid

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
        
        # generate a unique name for this specific request instance
        pod_name = f"{game}-{uuid.uuid4().hex[:8]}"

        # define the pod spec
        # the label 'app: rpslk-frontend' MUST match the Service selector
        pod_spec = client.V1Pod(
            metadata=client.V1ObjectMeta(
                name=pod_name,
                labels={
                    "app": "rpslk-frontend",
                    "managed-by": "vm-backend"
                },
                # clean up the pod object 60s after it finishes/dies
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

        # create the pod
        try:
            v1.create_namespaced_pod(namespace=namespace, body=pod_spec)
            print(f"Created pod {pod_name} with lifetime {lifetime}m")
        except client.exceptions.ApiException as e:
            raise Exception(f"Failed to create pod: {e}")

        # wait for pod to be Running and get IP
        print("Waiting for pod to get IP...")
        max_wait = 60  # timeout for pod startup
        start_time = time.time()

        while True:
            if time.time() - start_time > max_wait:
                # cleanup if stuck
                v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
                raise Exception("Could not create pod on time")

            try:
                pod_status = v1.read_namespaced_status(name=pod_name, namespace=namespace)
                
                if pod_status.status.phase == "Running" and pod_status.status.pod_ip:
                    #connection_string = "http://rpslk-frontend.vending-machine.svc.cluster.local:8080" # pod ip inside cluster

                    nodes = v1.list_node().items
                    node_ips = []

                    for node in nodes:
                        for address in node.status.addresses:
                            if address.type == "InternalIP":
                                node_ips.append(address.address)

                    #get the service port
                    service = core_api.read_namespaced_service(DEPLOYMENT_NAME, "default")
                    port = service.spec.ports[0].node_port

                    break
                
                if pod_status.status.phase in ["Failed", "Succeeded"]:
                    raise Exception("Pod creation failed")

            except client.exceptions.ApiException:
                pass
            
            time.sleep(1)

        return jsonify({"pod": pod_name, "status": "running", "ip": f"{random.choice(node_ips)}:{port}", "lifetime": lifetime})
    except Exception as e:
        return jsonify({"error": f"Internal error: {e}"}), 400

    return jsonify({"error": "Internal error"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
