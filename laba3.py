h = 8
m = 35

class Processor:
    def __init__(self):
        self.characteristic_bits_amount = h
        self.characteristic_bits_bias = (2 ** h // 2) - 1
        self.mantissa_bits_amount = m

        self.register_1 = None
        self.register_2 = None
        self.register_3 = None
        self.register_4 = None
        self.register_5 = None
        self.register_6 = None
        self.register_7 = None
        self.register_8 = None

        self.max_bound = 2 **(2**(self.characteristic_bits_amount-1))
        self.min_bound = -2 **(2**(self.characteristic_bits_amount-1))

    @staticmethod
    def print_to_console(s, h, m, num):
        return str(s) + ' ' + str(h) + ' ' + str(m) + ' Represents: ' + str(num)

    @staticmethod
    def invert_bits(num):
        inv_n = ''
        for n in num:
            if n == '1':
                inv_n = inv_n + '0'
            if n == '0':
                inv_n = inv_n + '1'
        return inv_n

    @staticmethod
    def decimal_converter(nu):
        while nu >= 1:
            nu /= 10.0
        return nu

    def dec_to_ieee754(self, number):
        if number is None:
            return None, '', ''
        if number > self.max_bound:
            raise Exception(f'Too positive number {number} for upper bound with h {self.characteristic_bits_amount}:'
                            f' {self.max_bound} 2^(-1)*2**{self.characteristic_bits_amount} - 1')
        if number < self.min_bound:
            raise Exception(f'Too negative number {number} for upper bound with h {self.characteristic_bits_amount}:'
                            f' {self.max_bound} 2^(-1)*2**{self.characteristic_bits_amount}')
        # convert 1E-7 form or 1E+10form types
        number = str(number)
        if number[1] == 'e':
            if number[2] == '-':
                n = '0.' + '0' * (int(number[3:]) - 1) + '1'
                if number[0] == '-':
                    number = '-' + n
                else:
                    number = n
            if number[2] == '+':
                n = '1' + '0' * (int(number[3:])) + '.0'
                if number[0] == '-':
                    number = '-' + n
                elif number[0] == '+':
                    number = n
        if '.' in number:
            whole, dec = number.split(".")
        else:
            whole = number
            dec = '0'
        h = 0
        whole = float(whole)
        if whole < 1:
            for i, dig in enumerate(dec):
                if dig != '0':
                    h = - i
                    break
        dec = float(dec)
        sign = '0'
        if whole < 0:
            sign = '1'
            whole = abs(whole)
        res = bin(int(whole)).lstrip("0b")
        sc_res = res
        if whole > 1:
            h_ = len(res) - 1
        else:
            h_ = h


        def decimal_converter(nu):
            while nu >= 1:
                nu /= 10
            return nu

        for x in range(self.mantissa_bits_amount):
            wd = str(float(decimal_converter(int(dec)) * 2))
            if '.' in wd:
                whole, dec = wd.split(".")
            else:
                whole = int(wd)
                dec = '0'
            dec = int(dec)
            sc_res = sc_res + str(whole)
        ch = bin(self.characteristic_bits_bias + h_).lstrip('0b')
        ch = '0' * (self.characteristic_bits_amount - len(ch)) + ch
        if sign == '0':
            num = int(sc_res, 2) * 2 ** (h - self.mantissa_bits_amount)
            return sign, ch, sc_res[:self.mantissa_bits_amount], num, h
        if sign == '1':
            num = - int(sc_res, 2) * 2 ** (h - self.mantissa_bits_amount)
            return sign, ch, sc_res[:self.mantissa_bits_amount], num, h
        else:
            return 0, '0' * self.characteristic_bits_amount, '0' * (self.mantissa_bits_amount - 1) + '1', 0, 0

    def mov(self, x):
        if x is not None:
            x = float(x)
            if self.min_bound < x < self.max_bound:
                self.register_8 = self.register_7
                self.register_7 = self.register_6
                self.register_6 = self.register_5
                self.register_5 = self.register_4
                self.register_4 = self.register_3
                self.register_3 = self.register_2
                self.register_2 = self.register_1
                self.register_1 = x
            else:
                if x > self.max_bound:
                    self.register_1 = float('inf')
                elif x < self.min_bound:
                    self.register_1 = float('-inf')
        else:
            return None

    def dubl(self):
        self.register_8 = self.register_7
        self.register_7 = self.register_6
        self.register_6 = self.register_5
        self.register_5 = self.register_4
        self.register_4 = self.register_3
        self.register_3 = self.register_2
        self.register_2 = self.register_1

    def swap(self):
        temp = self.register_1
        self.register_1 = self.register_2
        self.register_2 = temp

    def add(self):
        nw = self.register_1 + self.register_2
        nw_bit = self.dec_to_ieee754(nw)[3]

        if (self.register_1 == float("inf") and self.register_2 == float("-inf")) or \
                (self.register_1 == float("-inf") and self.register_2 == float("inf")):
            self.register_1 = float("nan")
        elif self.register_1 == float("inf") or self.register_2 == float("inf"):
            self.register_1 = float("inf")
        elif self.register_1 == float("-inf") or self.register_2 == float("-inf"):
            self.register_1 = float("-inf")
        else:
            if self.min_bound < nw < self.max_bound:
                self.register_1 = nw
                self.register_2 = self.register_3
                self.register_3 = self.register_4
                self.register_4 = self.register_5
                self.register_5 = self.register_6
                self.register_6 = self.register_7
                self.register_7 = self.register_8
                self.register_8 = None
            else:
                raise Exception(f'{self.register_1} + {self.register_2} = {nw} value not in bounds: '
                                f'{self.min_bound}, {self.max_bound}')
        if self.register_1 == float("inf") or self.register_1 == float("-inf") or self.register_1 == float("nan"):
            print(f"Result: {self.register_1}")
            return

    def sub(self):
        nw = self.register_1 - self.register_2
        nw = self.dec_to_ieee754(nw)[3]
        if self.min_bound < nw < self.max_bound:
            self.register_1 = self.dec_to_ieee754(nw)[3]
            self.register_2 = self.register_3
            self.register_3 = self.register_4
            self.register_4 = self.register_5
            self.register_5 = self.register_6
            self.register_6 = self.register_7
            self.register_7 = self.register_8
            self.register_8 = None
        else:
            raise Exception(f'{self.register_1} - {self.register_2} = {nw} value not in bounds:'
                            f'{self.min_bound}, {self.max_bound}')

    def mult(self):
        nw = self.register_1 * self.register_2
        nw = self.dec_to_ieee754(nw)[3]
        if self.min_bound < nw < self.max_bound:
            self.register_1 = self.dec_to_ieee754(nw)[3]
            self.register_2 = self.register_3
            self.register_3 = self.register_4
            self.register_4 = self.register_5
            self.register_5 = self.register_6
            self.register_6 = self.register_7
            self.register_7 = self.register_8
            self.register_8 = None
        else:
            raise Exception(f'{self.register_1} * {self.register_2} = {nw} value not in bounds:'
                            f'{self.min_bound}, {self.max_bound}')

    def div(self):
        if self.register_2 is not None and self.register_2 != 0:
            nw = self.register_1 / self.register_2
            if nw == float("inf") or nw == float("-inf") or nw > self.max_bound or nw < self.min_bound:
                self.register_1 = float("inf") if nw > 0 else float("-inf")
            else:
                self.register_1 = nw
                self.register_2 = self.register_3
                self.register_3 = self.register_4
                self.register_4 = self.register_5
                self.register_5 = self.register_6
                self.register_6 = self.register_7
                self.register_7 = self.register_8
                self.register_8 = None
        else:
            self.register_1 = float("inf") if self.register_1 > 0 else float("-inf")
        if self.register_1 == float("inf") or self.register_1 == float("-inf"):
            print(f"Result: {self.register_1}")
            return

    def ex_com(self, current_command, cl):
        print(f"Command № {cl // 2 + 1} clock rate {cl + 1}\n")
        parts = [p for p in current_command.split()]
        current_command = parts[0]
        register_1 = self.dec_to_ieee754(self.register_1)
        register_2 = self.dec_to_ieee754(self.register_2)
        register_3 = self.dec_to_ieee754(self.register_3)
        register_4 = self.dec_to_ieee754(self.register_4)
        register_5 = self.dec_to_ieee754(self.register_5)
        register_6 = self.dec_to_ieee754(self.register_6)
        register_7 = self.dec_to_ieee754(self.register_7)
        register_8 = self.dec_to_ieee754(self.register_8)
        print(f"1R: {register_1[0]} {register_1[1]} {register_1[2]}   {self.register_1}\n"
              f"2R: {register_2[0]} {register_2[1]} {register_2[2]}   {self.register_2}\n"
              f"3R: {register_3[0]} {register_3[1]} {register_3[2]}   {self.register_3}\n"
              f"4R: {register_4[0]} {register_4[1]} {register_4[2]}   {self.register_4}\n"
              f"5R: {register_5[0]} {register_5[1]} {register_5[2]}   {self.register_5}\n"
              f"6R: {register_6[0]} {register_6[1]} {register_6[2]}   {self.register_6}\n"
              f"7R: {register_7[0]} {register_7[1]} {register_7[2]}   {self.register_7}\n"
              f"8R: {register_8[0]} {register_8[1]} {register_8[2]}   {self.register_8}\n"
              '\n'
              f"IR: {current_command}")
        print()
        if current_command == 'load':
            if len(parts) != 2:
                raise Exception(f'PC {cl // 2 + 1} TC {cl + 1}')
            value = parts[1]
            self.mov(x=value)
        elif current_command == 'dubl':
            self.dubl()
        elif current_command == 'swap':
            self.swap ()
        elif current_command == 'add':
            self.add()
        elif current_command == 'sub':
            self.sub()
        elif current_command == 'mult':
            self.mult()
        elif current_command == 'div':
            self.div()
        else:
            raise Exception(f'Unknown command {parts[0]}')
        if self.register_1 in [float('inf'), -float('inf')]:
            return True
        print(f"Command № {cl // 2 + 1} clock rate {cl + 2}\n")
        register_1 = self.dec_to_ieee754(self.register_1)
        register_2 = self.dec_to_ieee754(self.register_2)
        register_3 = self.dec_to_ieee754(self.register_3)
        register_4 = self.dec_to_ieee754(self.register_4)
        register_5 = self.dec_to_ieee754(self.register_5)
        register_6 = self.dec_to_ieee754(self.register_6)
        register_7 = self.dec_to_ieee754(self.register_7)
        register_8 = self.dec_to_ieee754(self.register_8)
        print(f"1R: {register_1[0]} {register_1[1]} {register_1[2]}   {self.register_1}\n"
              f"2R: {register_2[0]} {register_2[1]} {register_2[2]}   {self.register_2}\n"
              f"3R: {register_3[0]} {register_3[1]} {register_3[2]}   {self.register_3}\n"
              f"4R: {register_4[0]} {register_4[1]} {register_4[2]}   {self.register_4}\n"
              f"5R: {register_5[0]} {register_5[1]} {register_5[2]}   {self.register_5}\n"
              f"6R: {register_6[0]} {register_6[1]} {register_6[2]}   {self.register_6}\n"
              f"7R: {register_7[0]} {register_7[1]} {register_7[2]}   {self.register_7}\n"
              f"8R: {register_8[0]} {register_8[1]} {register_8[2]}   {self.register_8}\n"
              '\n'
              f"IR: {current_command}")
        print()

    def run(self, commands):
        result_register = None
        computation_stopped = False
        for c, command in enumerate(commands):
            print('_' * 50)
            stop_computation = self.ex_com(current_command=command, cl=2 * c)
            if stop_computation:
                result_register = getattr(self, f"register_1")
                computation_stopped = True
                break
            result_register = getattr(self, f"register_1")
        print('_' * 50)
        if computation_stopped:
            if result_register == float('inf'):
                print('1R:0 11111111 000000000000000000000000000000000000    inf')
            elif result_register == -float('inf'):
                print('1R:1 11111111 000000000000000000000000000000000000    -inf')
        else:
            print('Result:')
            if result_register is not None:
                if result_register == float('inf'):
                    print('1R:0 11111111 000000000000000000000000000000000000    inf')
                elif result_register == -float('inf'):
                    print('1R:1 11111111 000000000000000000000000000000000000    -inf')
                else:
                    sign, ch, sc_res, num, h = self.dec_to_ieee754(result_register)
                    print(f'1R: {sign} {ch} {sc_res}   {result_register}')
        input()

def main():
    a = input("Введіть значення 'a': ")
    b = input("Введіть значення 'b': ")
    print("\nF=a-b+2.5/a-2.5/b")

    commands = [
        f'load {b}',
        f'load {a}',
        'load 2.5',
        'div',
        'swap',
        'load 2.5',
        'div',
        'sub',
        f'load {b}',
        f'load {a}',
        'sub',
        'add'
    ]

    proc = Processor()
    proc.run(commands)

if __name__ == '__main__':
    main()