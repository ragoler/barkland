import asyncio
import threading
import time

class DummyDog:
    def __init__(self, name):
        self.name = name

sandbox_clients = {}

def create_sandbox_for_dog(dog_name):
    # Simulate a blocking API call (e.g., 500ms provision)
    print(f"[{time.time():.4f}] Create sandbox started for {dog_name}")
    time.sleep(0.5) 
    sandbox_clients[dog_name] = "ready"
    print(f"[{time.time():.4f}] Create sandbox finished for {dog_name}")

async def run_simulation():
    dogs = {f"dog-{i}": DummyDog(f"dog-{i}") for i in range(5)}
    
    print(f"[{time.time():.4f}] --- START SPACING LOOP ---")
    for dog in dogs.values():
        if dog.name not in sandbox_clients:
             print(f"[{time.time():.4f}] Spawning thread for {dog.name}")
             threading.Thread(target=create_sandbox_for_dog, args=(dog.name,), daemon=True).start()
             await asyncio.sleep(0.05) # 50ms sleep
    print(f"[{time.time():.4f}] --- FINISHED SPACING LOOP ---")
    
    # Let threads finish
    await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_simulation())
