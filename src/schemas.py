from pydantic import BaseModel, Field, conint, validator
from typing import List, Optional


# axi bus
class AxiBus(BaseModel):
    width: Optional[int] = Field(4, description="AXI width in bytes")
    frequency: Optional[conint(ge=1000000)] = Field(
        1000000, description="AXI frequency in Hz (>= 1 MHz)"
    )


# cpucluster
class CPUCluster(BaseModel):
    arch_family: Optional[str] = Field(None, description="CPU architecture family e.g. ARMV8")
    cluster_name: Optional[str]
    cores_per_cluster: Optional[conint(ge=1)] = Field(
        None, description="Number of cores must be >= 1"
    )
    core_frequency_mhz: Optional[conint(ge=1)] = Field(
        None, description="CPU frequency in MHz"
    )


# soc
class SoC(BaseModel):
    short_name: str
    axi_bus: Optional[AxiBus]
    cpu_clusters: List[CPUCluster] = Field(default_factory=list)


# ecu
class ECU(BaseModel):
    short_name: str
    socs: List[SoC] = Field(default_factory=list)


# sys root
class SystemModel(BaseModel):
    ecus: List[ECU] = Field(default_factory=list)
