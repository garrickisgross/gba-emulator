from gb.instr_map import INSTRUCTION_MAP
from gb.mmu import GBMMU
from gb.timer import Timer

class GBCPU:
    A = 0
    F = 0
    B = 0
    C = 0
    D = 0
    E = 0
    H = 0
    L = 0
    SP = 0
    PC = 0
    running = True

    def __init__(self, mmu: GBMMU):
        self.mmu = mmu

    def reset(self, rom_bytes: bytes) -> None:
        self.A = 0
        self.F = 0
        self.B = 0
        self.C = 0
        self.D = 0
        self.E = 0
        self.H = 0
        self.L = 0
        self.SP = 0xFFFE
        self.PC = 0x0100
        self.running = True
        self.timer = Timer()

        self.load_rom(rom_bytes)

    get_BC = lambda self: (self.B << 8) | self.C
    set_BC = lambda self, value: (setattr(self, 'B', (value >> 8) & 0xFF), setattr(self, 'C', value & 0xFF))
    get_DE = lambda self: (self.D << 8) | self.E
    set_DE = lambda self, value: (setattr(self, 'D', (value >> 8) & 0xFF), setattr(self, 'E', value & 0xFF))
    get_HL = lambda self: (self.H << 8) | self.L
    set_HL = lambda self, value: (setattr(self, 'H', (value >> 8) & 0xFF), setattr(self, 'L', value & 0xFF))
    get_AF = lambda self: (self.A << 8) | self.F
    set_AF = lambda self, value: (setattr(self, 'A', (value >> 8) & 0xFF), setattr(self, 'F', value & 0xFF))

    BC = property(get_BC, set_BC)
    DE = property(get_DE, set_DE)
    HL = property(get_HL, set_HL)
    AF = property(get_AF, set_AF)

    def get_flags(self) -> dict:
        return {
            'Z': (self.F >> 7) & 1,
            'N': (self.F >> 6) & 1,
            'H': (self.F >> 5) & 1,
            'C': (self.F >> 4) & 1,
        }
    

    def set_flags(self, Z: int = None, N: int = None, H: int = None, C: int = None) -> None:
        if Z is not None:
            self.F = (self.F & ~(1 << 7)) | ((Z & 1) << 7)
        if N is not None:
            self.F = (self.F & ~(1 << 6)) | ((N & 1) << 6)
        if H is not None:
            self.F = (self.F & ~(1 << 5)) | ((H & 1) << 5)
        if C is not None:
            self.F = (self.F & ~(1 << 4)) | ((C & 1) << 4)


    def load_rom(self, rom_bytes: bytes) -> None:
        for i in range(min(len(rom_bytes), len(self.mmu.rom))):
            self.mmu.rom[i] = rom_bytes[i]

    def step(self) -> None:
        if not self.running:
            return
        instruction = self.mmu.read_byte(self.PC)
        self.PC += 1
        self.execute_instruction(instruction)

    def run(self) -> None:
        while self.running:
            self.step()

    def execute_instruction(self, instruction: int) -> None:
        if instruction in INSTRUCTION_MAP:
            INSTRUCTION_MAP[instruction](self)
        else:
            raise NotImplementedError(f"Instruction {instruction:02X} not implemented.")

    def read_byte(self) -> int: 
        byte = self.mmu.read_byte(self.PC)
        self.PC += 1
        return byte

    def write_byte(self, value: int) -> None: self.mmu.write_byte(self.PC, value)


        


