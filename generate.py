import sys
import json
import time

def generate_responses(prompt):
    # Simula la generación progresiva de respuestas
    for i in range(1, 6):
        response = f"Progreso {i}/5 para el prompt: {prompt}"
        yield response
        time.sleep(1)

if __name__ == "__main__":
    for line in sys.stdin:
        input_data = json.loads(line.strip())
        prompt = input_data.get("prompt")

        for response in generate_responses(prompt):
            print(json.dumps({"response": response}))
            sys.stdout.flush()
