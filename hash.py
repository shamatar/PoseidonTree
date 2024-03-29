import params

def poseidon_mimc(input):
    assert(len(input) == params.t)
    state = input
    round = 0
    r_f = params.r_f
    r_p = params.r_p
    for full_round in range(0, r_f):
        round_constants = params.full_round_keys[full_round*params.t:(full_round+1)*params.t]
        for i in range(0, params.t):
            state[i] = (state[i] + round_constants[i]) % params.modulus
            state[i] = params.sbox(state[i])
        
        new_state = [int(0)]*params.t
        for i in range(0, params.t):
            msd_row = params.msd[i*params.t:(i+1)*params.t]
            new_state[i] = scalar_product(state, msd_row)

        state = new_state
        round += 1

    for partial_round in range(0, r_p):
        round_constants = params.partial_round_keys[partial_round*params.t:(partial_round+1)*params.t]
        for i in range(0, params.t):
            state[i] = (state[i] + round_constants[i]) % params.modulus
            
        state[0] = params.sbox(state[0])
        
        new_state = [int(0)]*params.t
        for i in range(0, params.t):
            new_state[i] = scalar_product(state, params.msd[i*params.t:(i+1)*params.t])

        state = new_state
        round += 1

    for full_round in range(r_f, 2*r_f - 1):
        round_constants = params.full_round_keys[full_round*params.t:(full_round+1)*params.t]
        for i in range(0, params.t):
            state[i] = (state[i] + round_constants[i]) % params.modulus
            state[i] = params.sbox(state[i])
        
        new_state = [int(0)]*params.t
        for i in range(0, params.t):
            new_state[i] = scalar_product(state, params.msd[i*params.t:(i+1)*params.t])

        state = new_state
        round += 1

    full_round = 2*r_f - 1
    round_constants = params.full_round_keys[full_round*params.t:(full_round+1)*params.t]
    for i in range(0, params.t):
        state[i] = (state[i] + round_constants[i]) % params.modulus
        state[i] = params.sbox(state[i])
    
    return state
    

def scalar_product(a, b):
    assert(len(a) == len(b))
    c = int(0)
    for i in range(0, len(a)):
        c += (a[i] * b[i]) % params.modulus
    return c % params.modulus


def print_to_hex(vec):
    for i in range(0, len(vec)):
        hex_string = '0x{:02x}'.format(vec[i])
        print(hex_string)

def poseidon_hash(input):
    input = input
    num_cycles = len(input) // params.absorbtion_round_len
    if len(input) % params.absorbtion_round_len != 0:
        num_cycles += 1
    for _ in range(len(input), params.absorbtion_round_len * num_cycles):
        input.append(int(0))
    
    state = [int(0)]*params.t
    state = poseidon_mimc(state)

    for i in range(0, num_cycles):
        to_absorb = input[params.absorbtion_round_len*i:params.absorbtion_round_len*(i+1)]
        for k in range(0, params.absorbtion_round_len):
            state[k] = (state[k] + to_absorb[k]) % params.modulus
        state = poseidon_mimc(state)
    
    return state[:params.output_len]
    

if __name__ == "__main__":
    input = [int(0)]*params.absorbtion_round_len
    output = poseidon_hash(input)
    hex_string = '0x{:02x}'.format(output[0])
    print(hex_string)