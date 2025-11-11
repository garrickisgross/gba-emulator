from pathlib import Path

def main(rom_path: str) -> None:
    from gb.mmu import GBMMU
    from gb.cpu import GBCPU

    # Initialize MMU and CPU
    mmu = GBMMU()
    cpu = GBCPU(mmu)

    # Load ROM
    rom_bytes = Path(rom_path).read_bytes()
    cpu.reset(rom_bytes)

    # Run the CPU
    cpu.run()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_rom>")
        sys.exit(1)
    rom_path = sys.argv[1]
    main(rom_path)

