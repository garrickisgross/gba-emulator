
class GBMMU:
    rom = bytearray(0x8000)  # 32KB ROM
    vram = bytearray(0x2000)  # 8KB Video RAM
    eram = bytearray(0x2000)  # 8KB External RAM
    wram = bytearray(0x2000)  # 8KB Work RAM
    oam = bytearray(0xA0)     # 160B Object Attribute Memory
    io_ports = bytearray(0x80)  # 128B I/O Ports
    hram = bytearray(0x7F)    # 127B High RAM
    ie_register = 0x00        # Interrupt Enable Register

    ADDRESS_RANGES = {
        'rom': (0x0000, 0x7FFF),
        'vram': (0x8000, 0x9FFF),
        'eram': (0xA000, 0xBFFF),
        'wram': (0xC000, 0xDFFF),
        'oam': (0xFE00, 0xFE9F),
        'io_ports': (0xFF00, 0xFF7F),
        'hram': (0xFF80, 0xFFFE),
        'ie_register': (0xFFFF, 0xFFFF),
    }

    def read_byte(self, address: int) -> int:
        if 0x0000 <= address <= 0x7FFF:
            return self.rom[address]
        elif 0x8000 <= address <= 0x9FFF:
            return self.vram[address - 0x8000]
        elif 0xA000 <= address <= 0xBFFF:
            return self.eram[address - 0xA000]
        elif 0xC000 <= address <= 0xDFFF:
            return self.wram[address - 0xC000]
        elif 0xFE00 <= address <= 0xFE9F:
            return self.oam[address - 0xFE00]
        elif 0xFF00 <= address <= 0xFF7F:
            return self.io_ports[address - 0xFF00]
        elif 0xFF80 <= address <= 0xFFFE:
            return self.hram[address - 0xFF80]
        elif address == 0xFFFF:
            return self.ie_register
        else:
            raise ValueError(f"Invalid memory read at address {address:04X}")
        
    def write_byte(self, address: int, value: int) -> None:
        if 0x0000 <= address <= 0x7FFF:
            self.rom[address] = value
        elif 0x8000 <= address <= 0x9FFF:
            self.vram[address - 0x8000] = value
        elif 0xA000 <= address <= 0xBFFF:
            self.eram[address - 0xA000] = value
        elif 0xC000 <= address <= 0xDFFF:
            self.wram[address - 0xC000] = value
        elif 0xFE00 <= address <= 0xFE9F:
            self.oam[address - 0xFE00] = value
        elif 0xFF00 <= address <= 0xFF7F:
            self.io_ports[address - 0xFF00] = value
        elif 0xFF80 <= address <= 0xFFFE:
            self.hram[address - 0xFF80] = value
        elif address == 0xFFFF:
            self.ie_register = value
        else:
            raise ValueError(f"Invalid memory write at address {address:04X}")