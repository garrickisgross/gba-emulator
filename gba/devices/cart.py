from pathlib import Path
from typing import Optional

from gba.memory.map import MMU

class Cartridge:
    """Represents a GBA Cartridge (ROM file)."""

    def __init__(self):
        self.title: Optional[str] = None
        self.data: bytes = b""

    def load(self, path: str) -> None:
        p = Path(path)
        self.data = p.read_bytes()

        self.title = self.data[0xA0:0xAC].decode('ascii').rstrip('\0')

    def mount_into(self, mmu: MMU) -> None:
        if not self.data:
            raise Exception("Cartridge: No data loaded to mount.")

        size = min(len(self.data), len(mmu.rom.mem))
        mmu.rom.mem[0:size] = self.data[0:size]

    