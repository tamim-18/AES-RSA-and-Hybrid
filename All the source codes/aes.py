import util
import itertools
import math
import copy

MIX_COLUMN = [
    [0x02, 0x03, 0x01, 0x01],
    [0x01, 0x02, 0x03, 0x01],
    [0x01, 0x01, 0x02, 0x03],
    [0x03, 0x01, 0x01, 0x02]
]

INV_MIX_COLUMN = [
    [0x0e, 0x0b, 0x0d, 0x09],
    [0x09, 0x0e, 0x0b, 0x0d],
    [0x0d, 0x09, 0x0e, 0x0b],
    [0x0b, 0x0d, 0x09, 0x0e]
]

# this function is used to get the padded key
def get_padded_key(key, key_size=16):
    return util.get_padded_text(key, key_size)

# this function is used to get the padded plain text
def get_padded_plain_text(text):
    length = 16 * ((len(text) // 16) + (0 if len(text) % 16 == 0 else 1))
    return util.get_padded_text(text, length)

# this function is used to get the round keys
def get_round_keys(padded_key):
    # Key scheduling algorithm...
    words = util.get_words(padded_key)
    i = len(words)
    
    while i < 44:
        words.append(util.word_xor(words[i-4], util.g(i >> 2, util.SBOX, words[i-1]) if i % 4 == 0 else words[i-1]))
        i += 1
        
    return [list(itertools.chain.from_iterable(words[i:i+4])) for i in range(0, len(words), 4)]

# this function is used to mix the columns. It takes a predefined matrix and a state matrix as input. It returns the result matrix..
def mix_columns(predefined_matrix, state_matrix):
    res_matrix = copy.deepcopy(state_matrix)
    
    for i in range(len(state_matrix)):
        for j in range(len(state_matrix[i])):
            a, b, c, d = predefined_matrix[i]
            res_matrix[i][j] = util.galois_mul_byte(a, state_matrix[0][j]) ^    \
                               util.galois_mul_byte(b, state_matrix[1][j]) ^    \
                               util.galois_mul_byte(c, state_matrix[2][j]) ^    \
                               util.galois_mul_byte(d, state_matrix[3][j])

    return res_matrix

def encrypt(plain_text, key, key_size):
    pkey = get_padded_key(key, key_size)
    # pkey_matrix = util.transpose(util.split_list(util.get_byte_array(pkey), int(math.sqrt(key_size))))
    state_arrays__ = util.split_list(util.get_byte_array(get_padded_plain_text(plain_text)), 16)
    state_matrices = [util.transpose(util.split_list(arr, 4)) for arr in state_arrays__]
    round_key_matrices = [util.transpose(util.split_list(rkey, 4)) for rkey in get_round_keys(pkey)]
    cipher_matrices = []
    
    for state_matrix in state_matrices:
        cipher_matrix = copy.deepcopy(state_matrix)
        
        # Round 0 (Add round key)...        
        for ri in range(len(cipher_matrix)):
            cipher_matrix[ri] = util.word_xor(cipher_matrix[ri], round_key_matrices[0][ri])
            
        # Round 1 - 9...
        for round_no in range(1, 10):
            # Substitution...
            cipher_matrix = util.substitute_bytes_in_matrix(util.SBOX, cipher_matrix)
            
            # Shift row...
            for ri in range(len(cipher_matrix)):
                cipher_matrix[ri] = util.cyclic_shift(cipher_matrix[ri], -ri) # Negative offset -> left shift
            
            # Mix columns...
            cipher_matrix = mix_columns(MIX_COLUMN, cipher_matrix)
            # Add round key...
            for ri in range(len(cipher_matrix)):
                cipher_matrix[ri] = util.word_xor(cipher_matrix[ri], round_key_matrices[round_no][ri])

        # Round 10...
        # Every step except the "mix column" step...
       
        # Substitution...
        cipher_matrix = util.substitute_bytes_in_matrix(util.SBOX, cipher_matrix)
        
        # Shift row...
        for ri in range(len(cipher_matrix)):
            cipher_matrix[ri] = util.cyclic_shift(cipher_matrix[ri], -ri) # Negative offset -> left shift
            
        # Add round key...
        for ri in range(len(cipher_matrix)):
            cipher_matrix[ri] = util.word_xor(cipher_matrix[ri], round_key_matrices[10][ri])
        
        cipher_matrices.append(util.transpose(cipher_matrix)) # Transposing for the convenience of
                                                              # flattening the matrices...

    cipher_text_bytes = copy.deepcopy(cipher_matrices)
    
    while type(cipher_text_bytes[0]) == list:
        cipher_text_bytes = list(itertools.chain.from_iterable(cipher_text_bytes))
    
    cipher_text_chars = []
    
    for byte in cipher_text_bytes:
        cipher_text_chars.append(chr(byte))

    return "".join(cipher_text_chars)

def decrypt(cipher_text, key, key_size):
    pkey = get_padded_key(key, key_size)
    
    state_arrays__ = util.split_list(util.get_byte_array(get_padded_plain_text(cipher_text)), 16)
    state_matrices = [util.transpose(util.split_list(arr, 4)) for arr in state_arrays__]
    round_key_matrices = [util.transpose(util.split_list(rkey, 4)) for rkey in get_round_keys(pkey)]
    plain_text_matrices = []
    
    for state_matrix in state_matrices:
        plain_text_matrix = copy.deepcopy(state_matrix)
        
        # Round 0 (Add round key - 10)...
        for ri in range(len(plain_text_matrix)):
            plain_text_matrix[ri] = util.word_xor(plain_text_matrix[ri], round_key_matrices[10][ri])
            
        # Round 1-9...
        for round_no in range(9, 0, -1):
            # Inverse shift rows...
            for ri in range(len(plain_text_matrix)):
                plain_text_matrix[ri] = util.cyclic_shift(plain_text_matrix[ri], ri) # positive -> right shift

            # Inverse substitution bytes...
            plain_text_matrix = util.substitute_bytes_in_matrix(util.INV_SBOX, plain_text_matrix)
            
            # Add round key...
            for ri in range(len(plain_text_matrix)):
                plain_text_matrix[ri] = util.word_xor(plain_text_matrix[ri], round_key_matrices[round_no][ri])
                
            # Inverse column mix...
            plain_text_matrix = mix_columns(INV_MIX_COLUMN, plain_text_matrix)
            
        # Round 10...
        # Inverse shift rows...
        for ri in range(len(plain_text_matrix)):
            plain_text_matrix[ri] = util.cyclic_shift(plain_text_matrix[ri], ri)

        # Inverse substitution bytes...
        plain_text_matrix = util.substitute_bytes_in_matrix(util.INV_SBOX, plain_text_matrix)

        # Add round key
        for ri in range(len(plain_text_matrix)):
            plain_text_matrix[ri] = util.word_xor(plain_text_matrix[ri], round_key_matrices[0][ri])

        plain_text_matrices.append(util.transpose(plain_text_matrix))

    plain_text_bytes = copy.deepcopy(plain_text_matrices)
    
    while type(plain_text_bytes[0]) == list:
        plain_text_bytes = list(itertools.chain.from_iterable(plain_text_bytes))
    
    plain_text_chars = []
    
    for byte in plain_text_bytes:
        plain_text_chars.append(chr(byte))

    return ("".join(plain_text_chars)).rstrip()