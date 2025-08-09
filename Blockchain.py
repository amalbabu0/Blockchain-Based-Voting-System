import hashlib
import json
import os
from time import time

class Blockchain:
    def __init__(self, filename='blockchain.json'):
        self.filename = filename
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.chain = json.load(f)
            self.current_votes = []
        else:
            self.chain = []
            self.current_votes = []
            self.new_block(previous_hash='1', proof=100)
            self.save_chain()

    def save_chain(self):
        with open(self.filename, 'w') as f:
            json.dump(self.chain, f, indent=4)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'votes': self.current_votes,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.last_block),
        }
        self.current_votes = []
        self.chain.append(block)
        self.save_chain()
        return block

    def new_vote(self, voter_id, candidate):
        vote = {
            'voter_id': hashlib.sha256(str(voter_id).encode()).hexdigest(),
            'candidate': candidate,
        }
        self.current_votes.append(vote)
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
