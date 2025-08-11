import torch

for i in range(torch.cuda.device_count()):
    print(torch.cuda.get_device_properties(i).name)
import torch
import os

# Check CPUs
total_cpus = os.cpu_count()
print(f"Total CPU cores: {total_cpus}")

# Check GPUs
if torch.cuda.is_available():
    num_gpus = torch.cuda.device_count()
    print(f"Total GPUs: {num_gpus}")
    
    # List each GPU
    for i in range(num_gpus):
        gpu_name = torch.cuda.get_device_name(i)
        print(f"GPU {i}: {gpu_name}")
else:
    print("No CUDA GPUs available")

import psutil
import torch

def check_system_load():
    """Check current system resource usage"""
    print("=" * 50)
    print("🖥️  CURRENT SYSTEM USAGE")
    print("=" * 50)
    
    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    print(f"CPU Usage: {cpu_percent}% of {cpu_count} cores")
    print(f"Available CPU cores: ~{cpu_count - (cpu_count * cpu_percent / 100):.0f}")
    
    # Memory usage
    memory = psutil.virtual_memory()
    print(f"RAM Usage: {memory.percent}% ({memory.used/1e9:.1f}GB / {memory.total/1e9:.1f}GB)")
    print(f"Available RAM: {memory.available/1e9:.1f}GB")
    
    # GPU usage (if available)
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            allocated = torch.cuda.memory_allocated(i) / 1e9
            reserved = torch.cuda.memory_reserved(i) / 1e9
            total = torch.cuda.get_device_properties(i).total_memory / 1e9
            usage_percent = (allocated / total) * 100
            print(f"GPU {i}: {usage_percent:.1f}% used ({allocated:.1f}GB / {total:.1f}GB)")
    
    print("=" * 50)

# Run this before your simulation
check_system_load()