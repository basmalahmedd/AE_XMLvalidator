import re
from typing import Callable, Dict, Any
import json

def parse_int(value):
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        match = re.search(r"\d+", value)
        if match:
            return int(match.group())
    return 0
def enum_default(obj):
    if hasattr(obj, "value"):
        return obj.value
    raise TypeError

def create_cpu_cluster(**kwargs) -> Dict[str, Any]:
    short_name = kwargs.get("short_name") or kwargs.get("name")
    freq = parse_int(kwargs.get("frequency", 0))
    cores = parse_int(kwargs.get("cores_per_cluster", 0))
    return {
        "short_name": {"name": short_name},
        "frequency": {"value": freq},
        "cores_per_cluster": cores
    }

def add_chiplet(**kwargs) -> Dict[str, Any]:
    short_name = kwargs.get("short_name") or kwargs.get("name")
    axi = parse_int(kwargs.get("axi_bus", 0))
    freq = parse_int(kwargs.get("frequency", 0))
    eth = kwargs.get("ethernet_interface", "native")
    if isinstance(eth, dict) and "mode" in eth:
        eth = eth["mode"]
    if hasattr(eth, "value"):  
        eth = eth.value
    if isinstance(eth, bool):
        eth = "native" if eth else "simulated"
    ucie = kwargs.get("ucie_interface", "endpoint")
    if isinstance(ucie, dict) and "mode" in ucie:
        ucie = ucie["mode"]
    if hasattr(ucie, "value"):
        ucie = ucie.value
    return {
        "short_name": {"name": short_name},
        "axi_bus": {"value": axi},
        "frequency": {"value": freq},
        "ethernet_interface": {"mode": eth},
        "ucie_interface": {"mode": ucie}
    }

TOOL_REGISTRY: Dict[str, Callable[..., Dict[str, Any]]] = {
    "create_cpu_cluster": create_cpu_cluster,
    "add_chiplet": add_chiplet,
}

def select_tool(tool_name: str):
    return TOOL_REGISTRY.get(tool_name)