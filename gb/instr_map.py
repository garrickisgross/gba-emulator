from instructions import *

INSTRUCTION_MAP = {
    0x00: noop,
    0x01: LD_BC_n16,
    0x02: LD_BCaddr_A,
    0x03: INC_BC,
    0x04: INC_B,
    0x05: DEC_B,
    0x06: LD_B_n8,
    0x07: RLCA,
    0x08: LD_a16addr_SP,
    0x09: ADD_HL_BC,
    0x0A: LD_A_BCaddr,
    0x0B: DEC_BC,
    0x0C: INC_C,
    0x0D: DEC_C,
    0x0E: LD_C_n8,
    0x0F: RRCA,
    0x10: stop,
}
