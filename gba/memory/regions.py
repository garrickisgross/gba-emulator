from typing import Callable, Dict
from gba.memory.bus import Device

class ByteArrayRegion(Device):
    """Backed by a bytearray. For WRAM, VRAM, etc."""
    def __init__(self, name: str, size: int, readonly: bool = False):
        super().__init__(name)
        self.mem = bytearray(size)
        self.readonly = readonly

    def read8(self, addr: int) -> int:
        return self.mem[addr]

    def read16(self, addr: int) -> int:
        return (self.mem[addr] | (self.mem[addr + 1] << 8))

    def read32(self, addr: int) -> int:
        return (self.mem[addr] | (self.mem[addr + 1] << 8) | (self.mem[addr + 2] << 16) | (self.mem[addr + 3] << 24))

    def write8(self, addr: int, value: int) -> None:
        if self.readonly: return
        self.mem[addr] = value & 0xFF

    def write16(self, addr: int, value: int) -> None:
        if self.readonly: return
        self.mem[addr] = value & 0xFF
        self.mem[addr + 1] = (value >> 8) & 0xFF

    def write32(self, addr: int, value: int) -> None:
        if self.readonly: return
        self.mem[addr] = value & 0xFF
        self.mem[addr + 1] = (value >> 8) & 0xFF
        self.mem[addr + 2] = (value >> 16) & 0xFF
        self.mem[addr + 3] = (value >> 24) & 0xFF

class IORegisterBlock(Device):
    """
    Simple IO region: map address offsets to getter/setter callables.
    Use for 0x04000000.. IO area; devices can plug their registers here or expose their own blocks.
    """

    def __init__(self, name: str, size: int):
        super().__init__(name)
        self.size = size
        self.read8_map: Dict[int, Callable[[], int]] = {}
        self.write8_map: Dict[int, Callable[[int], None]] = {}

    def bind8(self, offset: int, read_fn: Callable[[], int], write_fn: Callable[[int], None]) -> None:
        self.read8_map[offset] = read_fn
        self.write8_map[offset] = write_fn
    
    def _rd8(self, addr: int) -> int:
        if addr in self.read8_map:
            return self.read8_map[addr]()
        else:
            raise Exception(f"IORegisterBlock {self.name}: No read8 bound at offset {addr:02X}")
        
    def _wr8(self, addr: int, value: int) -> None:
        if addr in self.write8_map:
            self.write8_map[addr](value)
        else:
            raise Exception(f"IORegisterBlock {self.name}: No write8 bound at offset {addr:02X}")
        
    def read8(self, addr: int) -> int:
        return self._rd8(addr)
    
    def read16(self, addr: int) -> int:
        lo = self._rd8(addr)
        hi = self._rd8(addr + 1)
        return lo | (hi << 8)
    
    def read32(self, addr: int) -> int:
        b0 = self._rd8(addr)
        b1 = self._rd8(addr + 1)
        b2 = self._rd8(addr + 2)
        b3 = self._rd8(addr + 3)
        return b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)
    
    def write8(self, addr: int, value: int) -> None:
        self._wr8(addr, value & 0xFF)

    def write16(self, addr: int, value: int) -> None:
        self._wr8(addr, value & 0xFF)
        self._wr8(addr + 1, (value >> 8) & 0xFF)
    
    def write32(self, addr: int, value: int) -> None:
        self._wr8(addr, value & 0xFF)
        self._wr8(addr + 1, (value >> 8) & 0xFF)
        self._wr8(addr + 2, (value >> 16) & 0xFF)
        self._wr8(addr + 3, (value >> 24) & 0xFF)

    
