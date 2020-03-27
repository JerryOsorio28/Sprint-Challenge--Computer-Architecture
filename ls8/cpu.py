"""CPU functionality."""

import sys

#OP CODES
LDI = 0b10000010 #130 / This instruction sets a specified register to a specified value.
PRN_REG = 0b01000111 #71 / Should print the value of a register
EIGHT = 0b00001000 #8 / Should print the number 8
HALT = 0b00000001 #1 / Halt the CPU (and exit the emulator).
ADD = 0b10100000 #160 / Add the value in two registers and store the result in registerA.
MUL = 0b10100010 #162 / Multiply the values in two registers together and store the result in registerA.
PUSH = 0b01000101 #69 / Push the value in the given register on the stack.
POP = 0b01000110 #70 / Pop the value from the top of the stack and store it in the PC.
CALL = 0b01010000 #80 / Calls a subroutine (function) at the address stored in the register.
RET = 0b00010001 #17 / Return from subroutine, Pop the value from the top of the stack and store it in the PC.
JEQ = 0b01010101 #85 / If equal flag is set (true), jump to the address stored in the given register.
CMP = 0b10100111 #167 / Compare the values in two registers.
JNE = 0b01010110 #86 / If E flag is clear (false, 0), jump to the address stored in the given register.
JMP = 0b01010100 #84 / Jump to the address stored in the given register.

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 #bytes of memory
        self.reg = [0] * 8 #register
        self.pc = 0 #program counter
        self.running = True
        self.sp = 7 #represents the eigth register

        # BRANCHTABLE
        self.branchtable = {
            ADD: self.add,
            MUL: self.mul,
            LDI: self.ldi,
            PRN_REG: self.prn_reg,
            HALT: self.halt,
            PUSH: self.push,
            POP: self.pop,
            CALL: self.call,
            RET: self.ret,
            JEQ: self.jeq,
            CMP: self.compare,
            JNE: self.jne,
            JMP: self.jmp,
        }

        # FLAGS
        self.flags = {
            'L': 0,
            'G': 0,
            'E': 0
        }
    
    def compare(self):
        reg_a = self.ram[self.pc + 1] 
        reg_b = self.ram[self.pc + 2]
        if self.reg[reg_a] == self.reg[reg_b]:
            self.flags['E'] = 1
        elif self.reg[reg_a] > self.reg[reg_b]:
            self.flags['G'] = 1
        elif self.reg[reg_a] < self.reg[reg_b]:
            self.flags['L'] = 1
        self.pc += 3

    def jeq(self):
        # If equal flag is set (true), jump to the address stored in the given register.
        reg = self.ram[self.pc + 1]
        # breakpoint()
        if self.flags['E'] == 1:
            self.pc = self.reg[reg]
        else:
            self.pc += 2

    def jne(self):
        # If E flag is clear (false, 0), jump to the address stored in the given register.
        reg = self.ram[self.pc + 1]
        if self.flags['E'] == 0:
            self.pc = self.reg[reg]
        else:
            self.pc += 2

    def jmp(self):
        reg = self.ram[self.pc + 1]
        self.pc = self.reg[reg]

    def ret(self):
        self.pc = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1

    def push(self):
        #  argument from our register
        reg = self.ram[self.pc + 1] 
        # copy the value in the give register
        val = self.reg[reg]
        # we decrement our stack pointer by 1 first
        self.reg[self.sp] -= 1
        # we set the value in our stack to be equal to the value given by our register
        self.ram[self.reg[self.sp]] = val
        self.pc += 2

    def pop(self):
        # value we are popping from the stack to the register
        reg = self.ram[self.pc + 1]
        # copy the value from the stack where the sp is pointing
        val = self.ram[self.reg[self.sp]]
        # we set the value in our register to be equal to the value given by our stack
        self.reg[reg] = val
        # then we increase our stack pointer by 1
        self.reg[self.sp] += 1
        self.pc += 2

    def add(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.reg[reg_a] += self.reg[reg_b]
        self.pc += 3
    
    def mul(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.reg[reg_a] *= self.reg[reg_b]
        self.pc += 3
    
    def ldi(self):        
        num = self.ram[self.pc + 1]
        reg = self.ram[self.pc + 2]
        self.reg[num] = reg
        self.pc += 3
    
    def prn_reg(self):
        reg = self.ram[self.pc + 1]
        print('reg', self.reg[reg])
        self.pc += 2
    
    def halt(self):
        self.running = False
    
    def call(self):
        # The address of the instruction directly after CALL is pushed onto the stack. 
        # This allows us to return to where we left off when the subroutine finishes executing.
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.pc + 2

        # The PC is set to the address stored in the given register. 
        # We jump to that location in RAM and execute the first instruction in the subroutine. 
        # The PC can move forward or backwards from its current location.
        reg = self.ram[self.pc + 1]
        self.pc = self.reg[reg]

    #should accept the address to read and return the value stored there.
    def ram_read(self, address):
        # print(self.ram[address])
        return self.ram[address]

    # should accept a value to write, and the address to write it to.
    def ram_write(self, address, value):
        self.ram[address] = value

    def load(self, filename):
        """Load a program into memory."""

        # pointer to iterate our program
        address = 0
        
        filename = sys.argv[1]

        try:
            with open(filename) as f:
                for line in f:

                    #  Ignore comments
                    comment_split = line.split('#')

                    # Strip whitespace
                    num = comment_split[0].strip()

                    # Ignore blank lines
                    if num == '':
                        continue

                    integer = int(num, 2)
                    self.ram[address] = integer
                    address += 1

        except FileNotFoundError:
            print('File not found')
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        # as long as the interpreter is running...
        while self.running:
            # iterates our ram array by index
            command = self.ram[self.pc]
            # checks if the command exists in our branchtable
            if command in self.branchtable.keys(): # LDI
                    # if it does, it runs the function associated with the opcode
                    self.branchtable[command]()
            else:
                print(f'Unknown instruction: {command}')
                sys.exit(1)