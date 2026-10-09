"""Read-only NVML inventory and process checks for explicit GPU/MIG UUIDs."""
import os
import pynvml as nvml


def _handle(selected):
    if not selected or "," in selected:
        raise ValueError("one explicitly selected CUDA device per job required")
    return (nvml.nvmlDeviceGetHandleByIndex(int(selected)) if selected.isdecimal()
            else nvml.nvmlDeviceGetHandleByUUID(selected))


def active_pids(selected):
    nvml.nvmlInit()
    try:
        return [row.pid for row in nvml.nvmlDeviceGetComputeRunningProcesses(_handle(str(selected)))]
    finally:
        nvml.nvmlShutdown()


def hardware(device):
    if device == "cpu": return dict(device="cpu", allocated_devices=0)
    selected=os.environ.get("CUDA_VISIBLE_DEVICES","0")
    nvml.nvmlInit()
    try:
        handle=_handle(selected)
        is_mig=bool(nvml.nvmlDeviceIsMigDeviceHandle(handle))
        parent=nvml.nvmlDeviceGetDeviceHandleFromMigDeviceHandle(handle) if is_mig else handle
        if not is_mig:
            try:
                if nvml.nvmlDeviceGetMigMode(handle)[0]:
                    raise ValueError("MIG-enabled parent requires an explicit MIG UUID")
            except nvml.NVMLError_NotSupported:
                pass
        attrs=nvml.nvmlDeviceGetAttributes(handle) if is_mig else None
        return dict(uuid=nvml.nvmlDeviceGetUUID(handle), parent_uuid=nvml.nvmlDeviceGetUUID(parent),
            name=nvml.nvmlDeviceGetName(handle), driver=nvml.nvmlSystemGetDriverVersion(),
            visible_devices=selected, allocated_devices=1, device_kind="mig_instance" if is_mig else "full_gpu",
            physical_index=nvml.nvmlDeviceGetIndex(parent), memory_total_bytes=nvml.nvmlDeviceGetMemoryInfo(handle).total,
            multiprocessor_count=attrs.multiprocessorCount if attrs else None,
            compute_capability=list(nvml.nvmlDeviceGetCudaComputeCapability(parent)),
            active_compute_pids_at_inspection=[p.pid for p in nvml.nvmlDeviceGetComputeRunningProcesses(handle)],
            parent_sm_clock_mhz=nvml.nvmlDeviceGetClockInfo(parent,nvml.NVML_CLOCK_SM),
            parent_power_watts=nvml.nvmlDeviceGetPowerUsage(parent)/1000)
    finally:
        nvml.nvmlShutdown()
