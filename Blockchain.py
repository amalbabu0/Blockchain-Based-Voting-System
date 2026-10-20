import hashlib
import json
import os
import uuid
from time import time

BLOB_API_URL = "https://vercel.com/api/blob"
BLOB_API_VERSION = "13"


def _store_id_from_token(token):
    parts = token.split("_")
    return parts[3] if len(parts) > 3 else ""


class Blockchain:
    """A toy vote ledger persisted as JSON.

    Vercel's filesystem is read-only, so local file I/O can't work there.
    When BLOB_READ_WRITE_TOKEN is set, the chain is read/written through
    Vercel Blob (shared across all serverless instances) instead of disk.
    """

    def __init__(self, filename='blockchain.json'):
        self.filename = filename
        self.blob_token = os.environ.get('BLOB_READ_WRITE_TOKEN')
        existing = self._read_raw()
        if existing is not None:
            self.chain = existing
            self.current_votes = []
        else:
            self.chain = []
            self.current_votes = []
            self.new_block(previous_hash='1', proof=100)
            self.save_chain()

    def _blob_headers(self, extra=None):
        headers = {
            "authorization": f"Bearer {self.blob_token}",
            "x-api-version": BLOB_API_VERSION,
            "x-vercel-blob-store-id": _store_id_from_token(self.blob_token),
            "x-api-blob-request-id": uuid.uuid4().hex,
        }
        if extra:
            headers.update(extra)
        return headers

    def _blob_url(self):
        store_id = _store_id_from_token(self.blob_token)
        return f"https://{store_id}.public.blob.vercel-storage.com/{self.filename}"

    def _read_raw(self):
        if self.blob_token:
            import requests
            resp = requests.get(self._blob_url(), timeout=15)
            if resp.status_code == 200:
                return resp.json()
            return None
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        return None

    def save_chain(self):
        if self.blob_token:
            import requests
            data = json.dumps(self.chain, indent=4).encode()
            resp = requests.put(
                f"{BLOB_API_URL}/",
                params={"pathname": self.filename},
                headers=self._blob_headers({
                    "x-vercel-blob-access": "public",
                    "x-add-random-suffix": "0",
                    "x-allow-overwrite": "1",
                    "x-content-type": "application/json",
                }),
                data=data,
                timeout=30,
            )
            resp.raise_for_status()
            return
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
