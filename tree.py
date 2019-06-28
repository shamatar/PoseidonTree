import hash
import params

class QuarticMerkleTree:
    def __init__(self, leafs):
        assert(len(leafs) % params.absorbtion_round_len == 0)
        depth = 0
        length = len(leafs)

        while length != 0:
            length = length // params.absorbtion_round_len
            depth += 1
        
        self.depth = depth

        self.levels = [[None]]*depth
        self.levels[0] = leafs
        for level in range(1, depth):
            chunks = len(self.levels[level-1]) // params.absorbtion_round_len
            self.levels[level] = [None]*chunks
        for level in range(1, depth):
            chunks = len(self.levels[level-1]) // params.absorbtion_round_len
            for chunk in range(0, chunks):
                input = self.levels[level-1][chunk*params.absorbtion_round_len:(chunk+1)*params.absorbtion_round_len]
                next_level_node = hash.poseidon_hash(input)[0]
                self.levels[level][chunk] = next_level_node

        assert(len(self.levels[depth-1]) == 1)

        self.root = self.levels[depth-1][0]

    def make_proof(self, leaf_index):
        proof = []
        index = leaf_index
        for level in range(0, self.depth - 1):
            start = (index // params.absorbtion_round_len) * params.absorbtion_round_len
            congruent = index % params.absorbtion_round_len
            end = start + params.absorbtion_round_len
            witness = []
            for witness_index in range(start, end):
                if witness_index == congruent:
                    continue
                witness.append(self.levels[level][witness_index])

            proof.append(witness)
            index = index // params.absorbtion_round_len

        return proof

    def check_proof(self, leaf, leaf_index, proof, root):
        current = leaf
        assert(len(proof) == self.depth - 1)
        index = leaf_index
        for level in range(0, self.depth - 1):
            congruent = index % params.absorbtion_round_len
            input = []
            k = 0
            for i in range(0, params.absorbtion_round_len):
                if i == congruent:
                    input.append(current)
                else:
                    input.append(proof[level][k])
                    k += 1
    
            current = hash.poseidon_hash(input)[0]
            index = index // params.absorbtion_round_len

        return current == root


if __name__ == "__main__":
    leafs = [int(0)]*params.absorbtion_round_len*4
    tree = QuarticMerkleTree(leafs)
    hex_string = '0x{:02x}'.format(tree.root)
    print(hex_string)
    proof = tree.make_proof(2)
    included = tree.check_proof(int(0), 2, proof, tree.root)
    assert(included)