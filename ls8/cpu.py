"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.registers = [0, 0, 0, 0, 0, 0, 0, 0xF4]
        self.pc = 0
        self.running = False
        self.sp = 7
        self.branch_table = {  # holds all commands
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100010: self.MUL,
            0b00000001: self.HLT,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b00010001: self.RET,
            0B01010000: self.CALL,
            0B10100111: self.CMP,
            0B01010101: self.JEQ,
            0B01010110: self.JNE,
            0B01010100: self.JMP,
            0B10101000: self.AND,
            0B10101010: self.OR,
            0B10101011: self.XOR,
            0B01101001: self.NOT,
            0B10101100: self.SHL,
            0B10101101: self.SHR,
            0B10100100: self.MOD
        }
        # flags is an 8 bit register, initialize at 0's
        self.flags = [0] * 8

    def load(self):
        """Load a program into memory."""

        address = 0
        if len(sys.argv) > 1:
            with open(sys.argv[1], 'r') as f:
                for current_line in f:
                    if current_line == "\n" or current_line[0] == "#":
                        continue
                    else:
                        self.ram[address] = int(current_line.split()[0], 2)

                    address += 1
        else:
            raise Exception('Enter a filename')

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
            self.pc += 3
        elif op == "MUL":  # multiply 2 values and save in the first register
            self.registers[self.ram[reg_a]] *= self.registers[self.ram[reg_b]]
            self.pc += 3
        # elif op == "SUB": etc
        elif op == "CMP":
            # CMP requires new register of flags, each possible comparison marks a different flag
            if self.registers[self.ram[reg_a]] > self.registers[self.ram[reg_b]]:
                self.flags[5] = 1
                self.flags[6] = 0
                self.flags[7] = 0
            elif self.registers[self.ram[reg_a]] < self.registers[self.ram[reg_b]]:
                self.flags[5] = 0
                self.flags[6] = 1
                self.flags[7] = 0
            elif self.registers[self.ram[reg_b]] == self.registers[self.ram[reg_a]]:
                self.flags[5] = 0
                self.flags[6] = 0
                self.flags[7] = 1

            self.pc += 3
        elif op == "AND":
            self.registers[self.ram[reg_a]] = self.registers[self.ram[reg_a]
                                                             ] & self.registers[self.ram[reg_b]]
            self.pc += 3
        elif op == "OR":
            self.registers[self.ram[reg_a]] = self.registers[self.ram[reg_a]
                                                             ] | self.registers[self.ram[reg_b]]
            self.pc += 3
        elif op == "XOR":
            self.registers[self.ram[reg_a]] = self.registers[self.ram[reg_a]
                                                             ] ^ self.registers[self.ram[reg_b]]
            self.pc += 3
        elif op == "NOT":
            self.registers[self.ram[reg_a]] = ~self.registers[self.ram[reg_a]]
            self.pc += 3
        elif op == "MOD":
            if self.registers[self.ram[reg_b]] == 0:
                raise Exception("Can not divide by 0")
            else:
                self.registers[self.ram[reg_a]] = self.registers[self.ram[reg_a]
                                                                 ] % self.registers[self.ram[reg_b]]
            self.pc += 3
        elif op = "SHR":
            self.registers[self.ram[reg_a]] = self.registers[self.ram[reg_a]
                                                             ] << self.registers[self.ram[reg_b]]
            self.pc += 3
        elif op == "SHL":
            self.registers[self.ram[reg_a]] = self.registers[self.ram[reg_a]
                                                             ] >> self.registers[self.ram[reg_b]]
            self.pc += 3
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.registers[i], end='')

        print()

    def ADD(self):
        self.alu("ADD", self.ram[self.pc+1], self.ram[self.pc+2])

    def HLT(self):
        self.running = False

    def LDI(self):  # Set the value of a register to an integer.
        reg = self.ram_read(self.pc+1)
        val = self.ram_read(self.pc+2)
        self.registers[reg] = val
        self.pc += 3

    def PRN(self):  # Print numeric value stored in the given register.
        reg = self.ram_read(self.pc+1)
        print(self.registers[reg])
        self.pc += 2

    # Multiply the values in two registers together and store the result in registerA.
    def MUL(self):
        self.alu("MUL", self.pc+1, self.pc+2)

    def PUSH(self):
        # Decrement SP
        self.registers[self.sp] -= 1
        # Get the reg num to push
        reg_number = self.ram[self.pc+1]
        # Get the value to push
        value = self.registers[reg_number]
        # Copy the value to the SP address
        self.ram[self.registers[self.sp]] = value
        # print(memory[0xea:0xf4])
        self.pc += 2

    def CALL(self):
        reg = self.ram[self.pc+1]
        address = self.registers[reg]
        return_address = self.pc + 2

        self.registers[7] -= 1
        sp = self.registers[7]

        self.ram[sp] = return_address

        self.pc = address

    def RET(self):
        sp = self.registers[7]
        return_address = self.ram[sp]
        self.registers[7] += 1

        self.pc = return_address

    # Pop the value at the top of the stack into the given register.
    def POP(self):
        # Get reg to pop into
        address = self.registers[self.sp]
        # Get the top of stack addr
        value = self.ram[address]
        # top_of_stack_addr = registers[self.sp]
        self.registers[self.ram[self.pc+1]] = value
        # Get the value at the top of the stack
        self.registers[self.sp] += 1
        # Store the value in the register
        # Increment the SP
        self.pc += 2

    def JMP(self):  # jump to designated register
        # read next line and jump to designated register
        new_line = self.registers[self.ram[self.pc+1]]
        # print(f"jump to line: {new_line}")
        self.pc = new_line

    def CMP(self):  # comparators, has3 options
        # call the ALU and send in next 2 lines
        self.alu("CMP", self.pc+1, self.pc+2)

    # If `E` flag is clear (false, 0), jump to the address stored in the given register.
    def JNE(self):
        if self.flags[7] == 0:
            # set PC to designated address
            self.pc = self.registers[self.ram[self.pc+1]]
        else:
            # since the flags werent set, skip next line
            self.pc += 2

    # If `equal` flag is set (true), jump to the address stored in the given register.
    def JEQ(self):
        if self.flags[7] == 1:
            self.pc = self.registers[self.ram[self.pc+1]]
        else:
            # if fla8 wasnt marked, skip next line
            self.pc += 2

    def AND(self):  # bitwise AND the values in reg_a and reg_b thenstore resulf in reg_a
        self.alu("AND", self.pc+1, self.pc+2)

    def OR(self):
        self.alu("OR", self.pc+1, self.pc+2)

    def XOR(self):
        self.alu("XOR", self.pc+1, self.pc+2)

    def NOT(self):
        self.alu("NOT", self.pc+1, self.pc+1)

    def SHL(self):
        self.alu("SHL", self.pc+1, self.pc+2)

    def SHR(self):
        self.alu("SHR", self.pc+1, self.pc+2)

    def MOD(self):
        self.alu("MOD", self.pc+1, self.pc+2)

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            # print(f"line#{self.pc}")
            command = self.ram_read(self.pc)
            if command in self.branch_table:
                self.branch_table[command]()
