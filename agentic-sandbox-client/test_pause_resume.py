import time
import sys
import os

# Adjust path to include the local client library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "agentic-sandbox-client")))

from k8s_agent_sandbox import SandboxClient
from kubernetes import client, config

def main():
    config.load_kube_config()
    core_api = client.CoreV1Api()
    
    print("Creating SandboxClient...")
    # Debug import source
    print(f"SandboxClient loaded from: {SandboxClient.__module__}")
    try:
         import inspect
         print(f"SandboxClient File: {inspect.getfile(SandboxClient)}")
    except Exception as e:
         print(f"Failed to get file: {e}")

    # Use Dev Mode (Port forward) to verify fully
    client_inst = SandboxClient(template_name="dog-agent-template", namespace="barkland")

    
    try:
        client_inst.__enter__()
        print(f"Sandbox claimed: {client_inst.claim_name}, Sandbox: {client_inst.sandbox_name}")
        
        # Verify Pod exists
        pod_name = client_inst.pod_name
        print(f"Underlying Pod: {pod_name}")
        pods = core_api.list_namespaced_pod(namespace="barkland", field_selector=f"metadata.name={pod_name}")
        if not pods.items:
             print("❌ ERROR: Pod not found before pause")
             return
        print("✅ Pod found running.")

        print("\n--- Testing .pause() ---")
        client_inst.pause()
        print("Paused called. Waiting for Pod deletion (up to 30s)...")
        
        for i in range(30):
             pods = core_api.list_namespaced_pod(namespace="barkland", field_selector=f"metadata.name={pod_name}")
             if not pods.items:
                  print("✅ Pod deleted successfully after pause (Scaled to 0).")
                  break
             # Also check if it's terminating
             p = pods.items[0]
             if p.metadata.deletion_timestamp:
                  print(f"Pod in deletion state: {p.status.phase}")
             time.sleep(1)
        else:
             print("❌ ERROR: Pod was not deleted within timeout.")

        print("\n--- Testing .resume() ---")
        client_inst.resume()
        print("Resume called. Waiting for general Sandbox Readyness updates (recreated pod)...")
        time.sleep(5) # Wait for scale-up reconciliation
        
        # Verify a NEW pod is born for the sandbox
        # Sandbox status or watcher reconciles and updates annotations but we can just use label selector or manual list
        all_pods = core_api.list_namespaced_pod(namespace="barkland")
        new_pod_found = False
        for p in all_pods.items:
             if p.metadata.name == client_inst.sandbox_name:
                  print(f"✅ Found NEW Pod recreated: {p.metadata.name} | Phase: {p.status.phase}")
                  new_pod_found = True
                  break

        
        if not new_pod_found:
             print("❌ ERROR: Recreated pod not found after resume.")
        
    finally:
        print("\nCleaning up...")
        client_inst.__exit__(None, None, None)
        print("Done.")

if __name__ == "__main__":
    main()
