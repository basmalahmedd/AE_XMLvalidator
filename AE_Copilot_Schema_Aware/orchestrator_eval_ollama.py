import json
import subprocess
import argparse
import time
import inspect
from pydantic import BaseModel, ValidationError
from rag_retriever import RagRetriever
import ae_xsd_schema
import tools

# -------------------- Helper --------------------
def enum_safe(obj):
    """Handle Enums and complex types during JSON serialization."""
    if hasattr(obj, "value"):
        return obj.value
    if isinstance(obj, (set, tuple)):
        return list(obj)
    return str(obj)

# -------------------- OLLAMA EXECUTION --------------------
def call_ollama(model: str, prompt: str, timeout: int = 180) -> str | None:
    """Run Ollama model with a prompt and return output text."""
    try:
        res = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return res.stdout.decode("utf-8", errors="ignore").strip()
    except subprocess.TimeoutExpired:
        print("Ollama timed out.")
        return None
    except Exception as e:
        print(f"Ollama error: {e}")
        return None

# -------------------- JSON HANDLING --------------------
def extract_json(text: str) -> dict | None:
    """Extract the first valid JSON object from model output."""
    if not text:
        return None
    try:
        start, end = text.find("{"), text.rfind("}") + 1
        if start == -1 or end == -1:
            raise ValueError("No JSON found.")
        snippet = text[start:end]
        return json.loads(snippet)
    except json.JSONDecodeError as e:
        print(f"JSON parse failed: {e}")
        return None
    except Exception as e:
        print(f"JSON extraction error: {e}")
        return None

# -------------------- TOOL-CALLING PROMPT --------------------
def build_prompt(user_query: str, schema_context: str) -> str:
    """Build a prompt that instructs the LLM to call a tool with arguments."""
    return f"""
You are an AI assistant that must call the correct tool for the user request.

Available tools:
- create_cpu_cluster(short_name, frequency, cores_per_cluster)
- add_chiplet(short_name, axi_bus, frequency, ethernet_interface, ucie_interface)

For each user request, output a single tool call as a JSON object in this format:
{{
  "tool": "tool_name",
  "args": {{
    "arg1": "value1",
    "arg2": "value2"
  }}
}}

Do not output explanations or comments. Output only valid JSON.

Schema Context (retrieved via RAG):
{schema_context}

User query:
{user_query}
"""

# -------------------- MODEL VALIDATION --------------------
def select_candidate_models(schema_context: str):
    """Select Pydantic models most relevant to the RAG schema context."""
    all_models = [
        cls for _, cls in inspect.getmembers(ae_xsd_schema, inspect.isclass)
        if issubclass(cls, BaseModel) and cls.__module__ == ae_xsd_schema.__name__
    ]
    candidates = [m for m in all_models if m.__name__.lower() in schema_context.lower()]
    return candidates or all_models

def validate_and_print(parsed: dict, schema_context: str):
    """Validate parsed JSON against schema and print clean output."""
    candidates = select_candidate_models(schema_context)
    for model in candidates:
        try:
            obj = model(**parsed)
            print(f"Validated → {model.__name__}")
            print(json.dumps(obj.model_dump(), indent=2, default=enum_safe))
            return True
        except ValidationError:
            continue
    print("Validation failed, raw data:")
    print(json.dumps(parsed, indent=2, default=enum_safe))
    return False

# -------------------- MAIN EXECUTION --------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Ollama model to use")
    args = parser.parse_args()

    retriever = RagRetriever()

    scenarios = {
        "S1_cluster": "Create a CPU cluster named C1 with frequency 2000000 Hz and 4 cores per cluster.",
        "S2_chiplet": "Add a GPU chiplet G1 with AXI bus width 64 bytes, frequency 1000000 Hz, ethernet interface simulated, and ucie interface in host mode.",
        "S3_cluster": "Create another CPU cluster named C2 with frequency 1500 MHz and 2 cores per cluster.",
        "S4_chiplet_multi": "Create an NPU chiplet N1 with AXI bus width 128 bytes, frequency 2000000 Hz, ethernet interface native, and ucie interface in endpoint mode.",
    }

    print(f"Testing model: {args.model}\n")

    for label, query in scenarios.items():
        print(f"--- {label} ---")
        start = time.time()

        schema_context = retriever.retrieve(query)
        prompt = build_prompt(query, schema_context)
        output = call_ollama(args.model, prompt)

        if not output:
            print("Failed to get JSON output.\n")
            continue

        parsed = extract_json(output)
        if not parsed or "tool" not in parsed or "args" not in parsed:
            print("Failed to extract tool call JSON.\n")
            print(output)
            continue

        tool_name = parsed["tool"]
        args_dict = parsed["args"]
        tool_func = tools.TOOL_REGISTRY.get(tool_name)

        if not tool_func:
            print(f"Tool '{tool_name}' not found in registry.\n")
            continue

        try:
            tool_result = tool_func(**args_dict)
            print(f"Tool executed: {tool_name}")
            validate_and_print(tool_result, schema_context)
        except Exception as e:
            print(f"Tool execution failed: {e}")

        print(f"Time: {round(time.time() - start, 2)}s\n")

if __name__ == "__main__":
    main()
