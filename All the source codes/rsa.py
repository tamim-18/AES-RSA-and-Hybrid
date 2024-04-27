
import random
import math

def isPrime(num):
    if num == 1 or num == 2:
        return True

    for i in range(2, num):
        if i*i > num:
            break
        
        if num % i == 0:
            return False
        
    return True
## desc: this function is used to get the modulo of a number. It takes three arguments, the number, the power, and the modulo. It returns the modulo of the number.
def fasModulo(num, p, mod):
    _p = 1
    val = num
    
    while _p < p:
        val = (val ** 2) % mod
        _p *= 2
        
    return val
## this method is used to get the powers of a number. It takes a number as an argument and returns the powers of the number.
def get_powers(d):
    powers = []
    p = 1
    
    while d > 0:
        if d & 0x01 != 0:
            powers.append(p)
        
        d >>= 1
        p <<= 1
    
    return powers

def get_prime_in_range(lbound, ubound):
   
    # that number and the num (+-) 1000.
    
    rnum = random.randint(lbound, ubound)
    prime_num = 0
    
    if ubound > 2**32:
        a = rnum
        rng = 0
        
        if (ubound - a) < 1000 and (a - lbound) < 1000:
            a = lbound
            rng = ubound - lbound
        elif (ubound - a) < 1000:
            rng = -1000
        elif (a - lbound) < 1000:
            rng = 1000
        else:
            rng = (1000 if random.randint(1, 100) > 50 else -1000) # Random condition to
                                                                   # ...randomize randomness :)

        b = a + rng
        
        for p in range(a, b+1, -1 if a > b else 1):
            if isPrime(p):
                prime_num = p
                break
    else:
        # For relatively smaller numbers, making a list to randomly choose a prime number
        # ... to make prime generation more random...
        prime_num_list = []
        
        for p in range(max(rnum - 1000, lbound), min(rnum + 1000,ubound) + 1):
            if isPrime(p):
                prime_num_list.append(p)
    
        prime_num = prime_num_list[random.randint(0, len(prime_num_list) - 1)]
    
    return prime_num

def key_gen(bit_length):
    MAX_VAL = (2**(bit_length // 2)) - 1
    MIN_VAL = 128

    p = get_prime_in_range(MIN_VAL, MAX_VAL)
    q = get_prime_in_range(MIN_VAL, MAX_VAL)
    
    while p == q:
        p = get_prime_in_range(MIN_VAL, MAX_VAL)
        q = get_prime_in_range(MIN_VAL, MAX_VAL)
        
    n = p*q
    phi_n = (p-1)*(q-1)
    ### Step - 4....
    e = 0
    
    for _e in range(2, phi_n):
        if math.gcd(_e, phi_n) == 1:
            e = _e
            break
    
    d = 0
    
    for i in range(1, (1 << 64)):
        if ((phi_n * i) + 1) % e == 0:
            d = ((phi_n * i) + 1) // e
            break
    
    return (e, n), (d, n)  # (Public key, Private key)

def encrypt(plain_text, public_key):
    cipher_values = []
    e, n = public_key
    
    for ch in plain_text:
        if ord(ch) < n:
            cipher_values.append((ord(ch) ** e) % n)
        else:
            cipher_values.append(ord(ch))
    
    return cipher_values

def decrypt(cipher_values, private_key):
    plain_chars = []
    d, n = private_key
    powers = get_powers(d)
    
    for value in cipher_values:
        ch_val = 1
        
        for p in powers:
            ch_val = (ch_val * fasModulo(value, p, n)) % n
            
        plain_chars.append(chr(ch_val))
        
    return "".join(plain_chars)

def decrypt_naive(cipher_values, private_key):
    plain_chars = []
    d, n = private_key
    
    for value in cipher_values:
        ch_val = (value ** d) % n
        plain_chars.append(chr(ch_val))
        
    return "".join(plain_chars)
