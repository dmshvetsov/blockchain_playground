from datetime import datetime
import hashlib
import json
from flask import Flask, jsonify


class Blockchain:
    def __init__(self) -> None:
        self.chain = []
        self.create_block(proof=1, previous_hash="0")
        self.proof_complexity = 4

    def create_block(self, proof: int, previous_hash: str):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(datetime.now()),
            "proof": proof,
            "previous_hash": previous_hash,
        }
        self.chain.append(block)
        return block

    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        while True:
            res_hash = hashlib.sha256(
                str(new_proof ** 2 - previous_proof ** 2).encode()
            ).hexdigest()
            if res_hash[:4] == ("0" * self.proof_complexity):
                break
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_valid(self):
        previous_block = self.chain[0]
        block_idx = 1
        while block_idx < len(self.chain):
            block = self.chain[block_idx]
            if block["previous_hash"] != self.hash(previous_block):
                return False
            res_hash = hashlib.sha256(
                str(block["proof"] ** 2 - previous_block["proof"] ** 2).encode()
            ).hexdigest()
            if res_hash[:4] != ("0" * self.proof_complexity):
                return False
            previous_block = block
            block_idx += 1
        return True

    def mine(self):
        previous_block = self.last_block()
        return self.create_block(
            self.proof_of_work(previous_block["proof"]), self.hash(previous_block)
        )


# API

app = Flask(__name__)

bc = Blockchain()


@app.route("/bc/mine", methods=["POST"])
def mine():
    block = bc.mine()
    return jsonify({"message": "successfully mined", "data": {"block": block}}), 201


@app.route("/bc", methods=["GET"])
def blockchain():
    return jsonify(data={"chain": bc.chain, "length": len(bc.chain)})


@app.route("/bc/valid", methods=["GET"])
def blockchain_valid():
    return jsonify(data={"valid": bc.is_valid()})
