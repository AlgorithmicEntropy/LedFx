import numpy as np

class Font3x3:

    def __init__(self) -> None:
        chars = {}    

        chars['A'] = np.array([
            [0,1,0],
            [1,1,1],
            [1,0,1],
        ])

        chars['B'] = np.array([
            [1,1,0],
            [1,1,1],
            [1,1,0],
        ])

        chars['C'] = np.array([
            [1,1,1],
            [1,0,0],
            [1,1,1],
        ])

        chars['D'] = np.array([
            [1,1,0],
            [1,0,1],
            [1,1,0],
        ])

        chars['E'] = np.array([
            [1,1,1],
            [1,1,0],
            [1,1,1],
        ])

        chars['F'] = np.array([
            [1,1,1],
            [1,1,0],
            [1,0,0],
        ])

        chars['G'] = np.array([
            [1,1,0],
            [1,0,1],
            [1,1,1],
        ])

        chars['H'] = np.array([
            [1,0,1],
            [1,1,1],
            [1,0,1],
        ])

        chars['I'] = np.array([
            [1,1,1],
            [0,1,0],
            [1,1,1],
        ])

        chars['J'] = np.array([
            [0,0,1],
            [0,0,1],
            [1,1,0],
        ])

        chars['K'] = np.array([
            [1,0,1],
            [1,1,0],
            [1,0,1],
        ])

        chars['L'] = np.array([
            [1,0,0],
            [1,0,0],
            [1,1,1],
        ])

        chars['M'] = np.array([
            [1,1,1],
            [1,1,1],
            [1,0,1],
        ])

        chars['N'] = np.array([
            [1,1,0],
            [1,0,1],
            [1,0,1],
        ])

        chars['O'] = np.array([
            [1,1,1],
            [1,0,1],
            [1,1,1],
        ])

        chars['P'] = np.array([
            [1,1,1],
            [1,1,1],
            [1,0,0],
        ])

        chars['Q'] = np.array([
            [1,1,1],
            [1,0,1],
            [1,1,0],
        ])

        chars['R'] = np.array([
            [1,1,0],
            [1,1,1],
            [1,0,1],
        ])

        chars['S'] = np.array([
            [0,1,1],
            [0,1,0],
            [1,1,0],
        ])

        chars['T'] = np.array([
            [1,1,1],
            [0,1,0],
            [0,1,0],
        ])

        chars['U'] = np.array([
            [1,0,1],
            [1,0,1],
            [1,1,1],
        ])

        chars['V'] = np.array([
            [1,0,1],
            [1,0,1],
            [0,1,0],
        ])

        chars['W'] = np.array([
            [1,0,1],
            [1,1,1],
            [1,1,1],
        ])

        chars['X'] = np.array([
            [1,0,1],
            [0,1,0],
            [1,0,1],
        ])

        chars['Y'] = np.array([
            [1,1,1],
            [0,1,0],
            [0,1,0],
        ])

        chars['Z'] = np.array([
            [1,1,0],
            [0,1,0],
            [0,1,1],
        ])

        chars['0'] = np.array([
            [1,1,1],
            [1,0,1],
            [1,1,1],
        ])

        chars['1'] = np.array([
            [1,1,0],
            [0,1,0],
            [1,1,1],
        ])

        chars['2'] = np.array([
            [1,1,0],
            [0,1,0],
            [0,1,1],
        ])

        chars['3'] = np.array([
            [1,1,0],
            [0,1,1],
            [1,1,0],
        ])

        chars['4'] = np.array([
            [1,0,1],
            [1,1,1],
            [0,0,1],
        ])

        chars['5'] = np.array([
            [0,1,1],
            [0,1,0],
            [1,1,0],
        ])

        chars['6'] = np.array([
            [1,0,0],
            [1,1,1],
            [1,1,1],
        ])

        chars['7'] = np.array([
            [1,1,1],
            [0,0,1],
            [0,0,1],
        ])

        chars['8'] = np.array([
            [1,1,1],
            [1,1,1],
            [1,1,1],
        ])

        chars['9'] = np.array([
            [1,1,1],
            [1,1,1],
            [0,0,1],
        ])

        chars['+'] = np.array([
            [0,1,0],
            [1,1,1],
            [0,1,0],
        ])

        chars['-'] = np.array([
            [0,0,0],
            [1,1,1],
            [0,0,0],
        ])

        chars['/'] = np.array([
            [0,0,1],
            [0,1,0],
            [1,0,0],
        ])

        chars['='] = np.array([
            [1,1,1],
            [0,0,0],
            [1,1,1],
        ])

        chars[','] = np.array([
            [0,0,0],
            [0,1,0],
            [0,1,0],
        ])

        chars['_'] = np.array([
            [0,0,0],
            [0,0,0],
            [1,1,1],
        ])

        chars['('] = np.array([
            [0,1,0],
            [1,0,0],
            [0,1,0],
        ])

        chars[')'] = np.array([
            [0,1,0],
            [0,0,1],
            [0,1,0],
        ])

        chars[':'] = np.array([
            [0,1,0],
            [0,0,0],
            [0,1,0],
        ])

        chars['?'] = np.array([
            [1,1,1],
            [0,1,1],
            [0,1,0],
        ])

        chars[' '] = np.array([
            [0,0,0],
            [0,0,0],
            [0,0,0],
        ])

        chars['%'] = np.array([
            [1,0,1],
            [0,1,0],
            [1,0,1],
        ])


        for key in chars:
            chars[key] = np.flip(chars[key], (0, 1))

        self.chars = chars

