from .bus import Bus
from .regions import ByteArrayRegion, IORegisterBlock

# Key GBA Regions
BIOS_START = 0x00000000; BIOS_SIZE = 16 * 1024
EWRAM_START = 0x02000000; EWRAM_SIZE = 256 * 1024
IWRAM_START = 0x03000000; IWRAM_SIZE = 32 * 1024
IO_START = 0x04000000; IO_SIZE = 0x400
PAL_START = 0x05000000; PAL_SIZE = 1 * 1024
VRAM_START = 0x06000000; VRAM_SIZE = 96 * 1024
OAM_START = 0x07000000; OAM_SIZE = 1 * 1024
ROM_START = 0x08000000; ROM_SIZE = 32 * 1024 * 1024  # Up to 32 MB


class MMU:
    def __init__(self):
        self.bus = Bus()
        
        # Create and map key memory regions
        self.bios = ByteArrayRegion("BIOS", bytearray(BIOS_SIZE))
        self.ewram = ByteArrayRegion("EWRAM", bytearray(EWRAM_SIZE))
        self.iwram = ByteArrayRegion("IWRAM", bytearray(IWRAM_SIZE))
        self.io = IORegisterBlock("IO", IO_SIZE)
        self.pal = ByteArrayRegion("PAL", bytearray(PAL_SIZE))
        self.vram = ByteArrayRegion("VRAM", bytearray(VRAM_SIZE))
        self.oam = ByteArrayRegion("OAM", bytearray(OAM_SIZE))
        self.rom = ByteArrayRegion("ROM", bytearray(ROM_SIZE))

        self.bus.map(BIOS_START, BIOS_SIZE, self.bios)
        self.bus.map(EWRAM_START, EWRAM_SIZE, self.ewram)
        self.bus.map(IWRAM_START, IWRAM_SIZE, self.iwram)
        self.bus.map(IO_START, IO_SIZE, self.io)
        self.bus.map(PAL_START, PAL_SIZE, self.pal)
        self.bus.map(VRAM_START, VRAM_SIZE, self.vram)
        self.bus.map(OAM_START, OAM_SIZE, self.oam)
        self.bus.map(ROM_START, ROM_SIZE, self.rom)
    
    # Convenience passthroughs
    def read8(self, addr: int) -> int: return self.bus.read8(addr)
    def read16(self, addr: int) -> int: return self.bus.read16(addr)
    def read32(self, addr: int) -> int: return self.bus.read32(addr)
    def write8(self, addr: int, value: int) -> None: return self.bus.write8(addr, value)
    def write16(self, addr: int, value: int) -> None: return self.bus.write16(addr, value)
    def write32(self, addr: int, value: int) -> None: return self.bus.write32(addr, value)
