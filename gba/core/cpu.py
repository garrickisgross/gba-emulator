from typing import List
from gba.memory.map import MMU

N_BIT = 31
Z_BIT = 30
C_BIT = 29
V_BIT = 28
T_BIT = 5 # 0= ARM, 1 = THUMB
MODE_MASK = 0x1F

COND_ALWAYS = 0xE

def _get_bit(value: int, bit: int) -> int:
    return (value >> bit) & 1

def _set_bit(value: int, bit: int, bit_value: int) -> int:
    if bit_value:
        return value | (1 << bit)
    else:
        return value & ~(1 << bit)
    
def bits(v: int, hi: int, lo: int) -> int:
    """Extract bits from v in range [lo, hi] (inclusive)."""
    mask = (1 << (hi - lo + 1)) - 1
    return (v >> lo) & mask

class CPU:
    def __init__(self, mmu: MMU, cpsr: int = 0x00000010):
        self.mmu = mmu
        self.cpsr = cpsr
        self.regs = [0] * 16  # R0-R15

    # CPSR Flag Helpers
    def get_n(self) -> int: return _get_bit(self.cpsr, N_BIT) 
    def get_z(self) -> int: return _get_bit(self.cpsr, Z_BIT)
    def get_c(self) -> int: return _get_bit(self.cpsr, C_BIT)
    def get_v(self) -> int: return _get_bit(self.cpsr, V_BIT)
    def get_t(self) -> int: return _get_bit(self.cpsr, T_BIT)
    def set_n(self, value: int) -> None: self.cpsr = _set_bit(self.cpsr, N_BIT, value)
    def set_z(self, value: int) -> None: self.cpsr = _set_bit(self.cpsr, Z_BIT, value)
    def set_c(self, value: int) -> None: self.cpsr = _set_bit(self.cpsr, C_BIT, value)          
    def set_v(self, value: int) -> None: self.cpsr = _set_bit(self.cpsr, V_BIT, value)
    def set_t(self, value: int) -> None: self.cpsr = _set_bit(self.cpsr, T_BIT, value)

    n = property(get_n, set_n)
    z = property(get_z, set_z)
    c = property(get_c, set_c)
    v = property(get_v, set_v)
    t = property(get_t, set_t)

    # --- PC Convenience ---
    def get_pc(self) -> int:
        return self.regs[15]
    
    def set_pc(self, value: int) -> None:
        self.regs[15] = value & 0xFFFFFFFC  # Align to 4 bytes

    pc = property(get_pc, set_pc)

    # ARM Peculiarity: reading PC during ARM execution returns address + 8
    def visible_pc(self) -> int:
        return (self.pc + 8) & 0xFFFFFFFF
    
    # --- Reset/Init ---
    def reset(self, start_pc: int) -> None:
        self.regs = [0] * 16
        self.pc = start_pc
        self.cpsr = 0x00000010  # System mode, ARM state
        

    # --- Fetch Helpers ---
    def fetch_32(self, addr: int) -> int:
        return self.mmu.read32(addr)
    

    # --- Condition Check (Simplified) ---
    def condition_passed(self, cond: int) -> bool:
        if cond == COND_ALWAYS:
            return True
        
        N, Z, C, V = self.n, self.z, self.c, self.v

        table = {
            0x0: Z == 1,               # EQ
            0x1: Z == 0,               # NE
            0x2: C == 1,               # CS/HS
            0x3: C == 0,               # CC/LO
            0x4: N == 1,               # MI
            0x5: N == 0,               # PL
            0x6: V == 1,               # VS
            0x7: V == 0,               # VC
            0x8: C == 1 and Z == 0,    # HI
            0x9: C == 0 or Z == 1,     # LS
            0xA: N == V,               # GE
            0xB: N != V,               # LT
            0xC: Z == 0 and N == V,    # GT
            0xD: Z == 1 or N != V,     # LE
        }

        return table.get(cond, True)
    
    # --- One ARM Step ---
    def step(self) -> int:
        if self.t:
            raise NotImplementedError("THUMB mode not implemented yet.")
        
        instr = self.fetch_32(self.pc)
        self.pc = (self.pc + 4) & 0xFFFFFFFF

        cond = bits(instr, 31, 28)
        if not self.condition_passed(cond):
            return 1
        
        c3 = bits(instr, 27, 25)
        if c3 == 0b101:
            return self._exec_branch(instr)
        elif c3 in (0b000, 0b001):
            return self._exec_data_proc(instr)
        elif c3 in (0b010, 0b011):
            return self._exec_ldr_str(instr)
        elif (instr & 0x0FFFFFF0) == 0x012FFF10:
            return self._exec_branch_exchange(instr)
        else:
            # For now, treat as a NOP
            return 1
        
    def _exec_branch(self, instr: int) -> int:
        link = (instr >> 24) & 1
        imm24 = instr & 0x00FFFFFF
        if imm24 & 0x00800000:
            imm = ((imm24 | 0xFF000000) << 2) & 0xFFFFFFFF
        else:
            imm = (imm24 << 2) & 0xFFFFFFFF
        
        next_pc = (self.pc + imm) & 0xFFFFFFFF
        if link:
            self.regs[14] = self.pc  # LR = address of next instruction
        self.pc = next_pc
        return 3 # Rough cycle count
    
    def _exec_bx(self, instr: int) -> int:
        rn = instr & 0xF
        target = self.regs[rn]
        self.pc = target & ~1
        self.t = target & 1
        return 3 # Rough cycle count
         
    def _exec_data_proc(self, instr: int) -> int:
        # Minimal subset for now
        opcode = bits(instr, 24, 21)
        S = (instr >> 20) & 1
        rn = bits(instr, 19, 16)
        rd = bits(instr, 15, 12)
        I = (instr >> 25) & 1

        if I:
            # Immediate with rotate (ignored for now)
            imm8 = instr & 0xFF
            rot = bits(instr, 11, 8) * 2
            op2 = ((imm8 >> rot) | (imm8 << (32 - rot))) & 0xFFFFFFFF

        else: 
            # TODO: Register shifter operand
            return 1
        
        match opcode:
            case 0x0: # AND
                self.regs[rd] = self.regs[rn] & op2
            case 0x1: # EOR
                self.regs[rd] = self.regs[rn] ^ op2
            case 0x2: # SUB
                self.regs[rd] = (self.regs[rn] - op2) & 0xFFFFFFFF
            case 0x3: # RSB
                self.regs[rd] = (op2 - self.regs[rn]) & 0xFFFFFFFF
            case 0x4: # ADD
                self.regs[rd] = (self.regs[rn] + op2) & 0xFFFFFFFF
            case 0x5: # ADC
                self.regs[rd] = (self.regs[rn] + op2 + self.c) & 0xFFFFFFFF
            case 0x6: # SBC
                self.regs[rd] = (self.regs[rn] - op2 - (1 - self.c)) & 0xFFFFFFFF
            case 0x7: # RSC
                self.regs[rd] = (op2 - self.regs[rn] - (1 - self.c)) & 0xFFFFFFFF
            case 0x8: # TST
                self.flags = self._update_flags(self.regs[rn] & op2)
            case 0x9: # TEQ
                self.flags = self._update_flags(self.regs[rn] ^ op2)
            case 0xA: # CMP
                self.flags = self._update_flags((self.regs[rn] - op2) & 0xFFFFFFFF)
            case 0xB: # CMN
                self.flags = self._update_flags((self.regs[rn] + op2) & 0xFFFFFFFF)
            case 0xC: # ORR
                self.regs[rd] = self.regs[rn] | op2
            case 0xD: # MOV
                self.regs[rd] = op2
            case 0xE: # BIC
                self.regs[rd] = self.regs[rn] & ~op2
            case 0xF: # MVN
                self.regs[rd] = ~op2 & 0xFFFFFFFF
            case _:
                return 1  # Unhandled opcode, treat as NOP

    def _update_flags(self, result: int) -> None:
        self.n = 1 if (result & 0x80000000) else 0
        self.z = 1 if (result == 0) else 0
        # C and V updates are ignored for now

    def _exec_ldr_str(self, instr: int) -> int:
        # stub for now
        return 1
    


