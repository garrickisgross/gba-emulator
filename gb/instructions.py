from gb.cpu import GBCPU
from gb.utils import get_carry, get_half_carry

def noop(cpu: GBCPU):
    cpu.timer.cycle(4)
    pass

def stop(cpu: GBCPU):
    cpu.running = False
    cpu.timer.cycle(4)

def LD_BC_n16(cpu: GBCPU):
    low = cpu.read_byte(cpu.PC)
    high = cpu.read_byte(cpu.PC)
    cpu.BC = (high << 8) | low
    cpu.timer.cycle(12)

def LD_BCaddr_A(cpu: GBCPU):
    address = cpu.BC
    cpu.mmu.write_byte(address, cpu.A)
    cpu.timer.cycle(8)

def LD_BCaddr_A(cpu: GBCPU):
    address = cpu.BC
    cpu.A = cpu.read_byte(address)
    cpu.timer.cycle(8)

def INC_BC(cpu: GBCPU):
    cpu.BC = (cpu.BC + 1) & 0xFFFF
    cpu.timer.cycle(8)

def INC_B(cpu: GBCPU):
    cpu.B = (cpu.B + 1) & 0xFF
    cpu.set_flags(Z=1 if cpu.B == 0 else 0, N=0)
    # Half-carry flag
    if (cpu.B & 0x0F) == 0x00:
        cpu.set_flags(H=1)
    else:
        cpu.set_flags(H=0)

    cpu.timer.cycle(4)

def DEC_B(cpu: GBCPU):
    cpu.B = (cpu.B - 1) & 0xFF
    cpu.set_flags(Z=1 if cpu.B == 0 else 0, N=1)

    # Half-carry flag
    if (cpu.B & 0x0F) == 0x0F:
        cpu.set_flags(H=1)
    else:
        cpu.set_flags(H=0)

    cpu.timer.cycle(4)

def LD_B_n8(cpu: GBCPU):
    cpu.B = cpu.read_byte(cpu.PC)
    cpu.timer.cycle(8)

def RLCA(cpu: GBCPU):
    # Rotate A left. Old bit 7 to Carry flag.
    old_bit7 = (cpu.A >> 7) & 0x01
    cpu.A = ((cpu.A << 1) | old_bit7) & 0xFF
    cpu.set_flags(Z=0, N=0, H=0, C=old_bit7)
    cpu.timer.cycle(4)

def LD_a16addr_SP(cpu: GBCPU):
    low = cpu.read_byte(cpu.PC)
    high = cpu.read_byte(cpu.PC)
    new_sp = cpu.SP & 0xFF
    addr = (high << 8) | low
    cpu.mmu.write_byte(addr, new_sp)
    cpu.mmu.write_byte(addr + 1, (cpu.SP >> 8) & 0xFF)
    cpu.timer.cycle(20)

def ADD_HL_BC(cpu: GBCPU):
    will_carry = get_carry(cpu.HL, cpu.BC)
    will_half_carry = get_half_carry(cpu.HL, cpu.BC)
    cpu.HL = cpu.HL + cpu.BC
    cpu.set_flags(N=0, H=will_half_carry, C=will_carry)
    cpu.timer.cycle(8)

def LD_A_BCaddr(cpu: GBCPU):
    byte = cpu.mmu.read_byte(cpu.BC)
    cpu.A = byte
    cpu.timer.cycle(8)

def DEC_BC(cpu: GBCPU):
    BC -= 1
    cpu.timer.cycle(8)

def INC_C(cpu: GBCPU):
    hc = get_half_carry(cpu.C, 1)
    cpu.C += 1

    if cpu.C == 0:
        z = 1
        cpu.set_flags(Z=z)

    cpu.set_flags( N=0, H=hc)
    cpu.timer.cycle(4)

def DEC_C(cpu: GBCPU):

    hc = get_half_carry(cpu.C, -1)
    cpu.C -= 1

    if cpu.C == 0:
        z = 1
        cpu.set_flags(z)

    cpu.set_flags(N=1, H=hc)
    cpu.timer.cycle(4)

def LD_C_n8(cpu: GBCPU):

    val = cpu.read_byte()
    cpu.C = val

def RRCA(cpu: GBCPU):
    rotated_bit = cpu.A & 0x01
    cpu.A = (cpu.A >> 1) | (rotated_bit << 7)
    cpu.set_flags(Z=0, N=0, H=0, C=rotated_bit)
    cpu.timer.cycle(4)
    










    








