from src.ae_xsd_schema import ArPackage
from pydantic import ValidationError

example_json = {
  "elements": [
    {
      "ecus": [
        {
          "short_name": {
            "name": "ECU_1"
          },
          "so_cs": [
            {
              "short_name": {
                "name": "SoC_1"
              },
              "axi_bus": {
                "width": 256,
                "frequency": 1000000
              },
              "ethernet_interface": {
                "mode": "simulated"
              },
              "ucie_interface": {
                "mode": "host",
                "Endpoint_DMA_Configuration": {
                  "Frequency": 110
                }
              },
              "cpu_cluster": {
                "operating_system": {
                  "Linux": {
                    "Show_UART_Terminal": True,
                    "Ubuntu_File_System": "22.04"
                  }
                },
                "arch_family": "ARMV8",
                "cluster_name": "MainCortex",
                "cores_per_cluster": 4,
                "core_frequency_mhz": 2000
              }
            }
          ]
        },
        {
          "short_name": {
            "name": "ECU_2"
          },
          "so_cs": [
            {
              "short_name": {
                "name": "SoC_2_1"
              },
              "axi_bus": {
                "width": 128,
                "frequency": 2000000
              },
              "ethernet_interface": {
                "mode": "native"
              },
              "ucie_interface": {
                "mode": "endpoint",
                "Endpoint_DMA_Configuration": {
                  "Frequency": 120
                }
              },
              "cpu_cluster": {
                "operating_system": {
                  "Linux": {
                    "Show_UART_Terminal": False,
                    "Buildroot_File_System": "2024.02"
                  }
                },
                "arch_family": "ARMV7",
                "cluster_name": "SecondaryCortex",
                "cores_per_cluster": 2,
                "core_frequency_mhz": 1000
              }
            }
          ]
        }
      ],
      "hw_sw_mapping": [
        {
          "cluster_ref": "/ECU_1/SoC_1/CPU_Cluster/MainCortex",
          "cluster_prebuilt_apps": [
            {
              "PrebuiltApplicationRef": "/apps/prebuilt-app-A"
            }
          ],
          "core_prebuilt_apps": [
            {
              "CoreId": 1,
              "PrebuiltApplicationRef": "/apps/prebuilt-app-B"
            }
          ],
          "core_runnables": [
            {
              "CoreId": 2,
              "RunnableRef": "/App_SW_Component/Internal_Behavior/Runnable",
              "Load": 25000,
              "Priority": 20
            }
          ]
        }
      ]
    }
  ]
}


try:
    pkg = ArPackage(**example_json)
    print(" JSON is valid")
    print(pkg)
except ValidationError as e:
    print("JSON invalid:", e.json(indent=2))
