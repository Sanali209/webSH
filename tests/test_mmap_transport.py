import pytest
import asyncio
import pyarrow as pa
import pyarrow.ipc as ipc
from multiprocessing import shared_memory
from plugins.system_transport.backend import SystemTransportPlugin, AllocParams, FreeParams

@pytest.fixture
def transport():
    plugin = SystemTransportPlugin()
    yield plugin
    plugin.on_shutdown()

@pytest.mark.asyncio
async def test_transport_alloc_free(transport):
    # 1. Alloc
    params = AllocParams(size=1024)
    result = await transport.alloc(params, None)
    assert "name" in result
    shm_name = result["name"]
    
    # Check if segment exists
    shm = shared_memory.SharedMemory(name=shm_name)
    assert shm.size >= 1024
    shm.close()
    
    # 2. Free
    free_result = await transport.free(FreeParams(name=shm_name), None)
    assert free_result["status"] == "success"
    
    # Check if segment is gone
    with pytest.raises(FileNotFoundError):
        shared_memory.SharedMemory(name=shm_name)

@pytest.mark.asyncio
async def test_arrow_zero_copy(transport):
    # 1. Create a large Arrow table
    data = [
        pa.array([i for i in range(100000)]),
        pa.array([f"item_{i}" for i in range(100000)])
    ]
    table = pa.Table.from_arrays(data, names=["id", "name"])
    
    # 2. Calculate size needed for IPC
    sink = pa.BufferOutputStream()
    with ipc.new_file(sink, table.schema) as writer:
        writer.write_table(table)
    buf = sink.getvalue()
    size = len(buf)
    
    # 3. Alloc shared memory
    alloc_result = await transport.alloc(AllocParams(size=size), None)
    shm_name = alloc_result["name"]
    
    # 4. Write to shared memory 
    shm = shared_memory.SharedMemory(name=shm_name)
    data_to_write = buf.to_pybytes()
    
    # Use cast('B') to ensure flat byte structure for assignment
    shm.buf[:size] = memoryview(data_to_write).cast('B')
    
    # 5. Read back from shared memory (Zero-copy)
    # This simulates another plugin reading the memory
    shm_consumer = shared_memory.SharedMemory(name=shm_name)
    
    # Create Arrow buffer directly from SHM memoryview
    arrow_buf = pa.py_buffer(shm_consumer.buf[:size])
    
    # Open the table from the buffer
    with ipc.open_file(arrow_buf) as reader:
        read_table = reader.read_all()
    
    assert read_table.num_rows == 100000
    assert read_table.column("id")[0].as_py() == 0
    
    # Cleanup: must delete arrow objects that hold references to SHM 
    # before we can close the SHM segment on some systems (Windows)
    del read_table
    del reader
    del arrow_buf
    import gc
    gc.collect()
    
    shm.close()
    shm_consumer.close()
    await transport.free(FreeParams(name=shm_name), None)

@pytest.mark.asyncio
async def test_large_transfer_perf(transport):
    import time
    # Allocate 100MB
    size = 100 * 1024 * 1024
    start = time.time()
    result = await transport.alloc(AllocParams(size=size), None)
    end = time.time()
    
    # Allocation should be very fast, but allow some margin for CI/system lag
    assert (end - start) < 0.5
    
    shm_name = result["name"]
    await transport.free(FreeParams(name=shm_name), None)
