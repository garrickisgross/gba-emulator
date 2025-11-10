from typing import Callable, List, Tuple

ReadFn8 = Callable[[int], int]
ReadFn16 = Callable[[int], int]
ReadFn32 = Callable[[int], int]
WriteFn8 = Callable[[int, int], None]
WriteFn16 = Callable[[int, int], None]
WriteFn32 = Callable[[int, int], None]

class Device:
    def __init__(self, name: str):
        self.name = name

    # Override these if you want the device to consume the address with an internal base
    def read8(self, addr: int) -> int: raise NotImplementedError
    def read16(self, addr: int) -> int: raise NotImplementedError
    def read32(self, addr: int) -> int: raise NotImplementedError
    def write8(self, addr: int, value: int) -> None: raise NotImplementedError
    def write16(self, addr: int, value: int) -> None: raise NotImplementedError
    def write32(self, addr: int, value: int) -> None: raise NotImplementedError


class Bus:
    """Routes reads/writes to registered devices based on address ranges."""

    def __init__(self):
        self._map: List[Tuple[int, int, Device, int]] = []
        self._open_bus = 0

    def map(self, start: int, size: int, dev: Device, base: int = 0) -> None:
        end = start + size - 1
        self._map.append((start, end, dev, base))

    def _route(self, addr: int) -> Tuple[Device, int]:
        for start, end, dev, base in self._map:
            if start <= addr <= end:
                return dev, addr - start + base
        raise Exception(f"Bus: No device mapped at address {addr:08X}")
    
    # ------------------ READS ---------------------
    def read8(self, addr: int) -> int:
        dev, routed_addr = self._route(addr)
        value = dev.read8(routed_addr)
        self._open_bus = value
        return value
    
    def read16(self, addr: int) -> int:
        dev, routed_addr = self._route(addr)
        value = dev.read16(routed_addr)
        self._open_bus = value & 0xFF
        return value
    
    def read32(self, addr: int) -> int:
        dev, routed_addr = self._route(addr)
        value = dev.read32(routed_addr)
        self._open_bus = value & 0xFF
        return value
    
    # ------------------ WRITES ---------------------

    def write8(self, addr: int, value: int) -> None:
        dev, routed_addr = self._route(addr)
        dev.write8(routed_addr, value & 0xFF)

    def write16(self, addr: int, value: int) -> None:
        dev, routed_addr = self._route(addr)
        dev.write16(routed_addr, value & 0xFFFF)

    def write32(self, addr: int, value: int) -> None:
        dev, routed_addr = self._route(addr)
        dev.write32(routed_addr, value & 0xFFFFFFFF)
    
    def open_bus(self) -> int:
        return self._open_bus