from gba.memory.map import MMU, ROM_START
from gba.devices.cart import Cartridge
from gba.core.cpu import CPU

def main(rom_path: str, start_pc: int = ROM_START) -> None:
    # Initialize MMU
    mmu = MMU()

    # Load and mount cartridge
    cart = Cartridge()
    cart.load(rom_path)
    cart.mount_into(mmu)
    


    cpu = CPU(mmu)
    cpu.reset(ROM_START)

    seen_pcs = set()
    for step in range(32):
        pc = cpu.pc
        instr = mmu.read32(pc)
        print(f"Step {step:02}: PC={pc:08X} INSTR={instr:08X}")
        cpu.step()


        if cpu.pc in seen_pcs:
            print(f"Detected loop at PC={cpu.pc:08X}, halting execution.")
            break

        seen_pcs.add(cpu.pc)





if __name__ == "__main__": 
    import sys
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_rom>")
        sys.exit(1)
    
    rom_path = sys.argv[1]
    main(rom_path)