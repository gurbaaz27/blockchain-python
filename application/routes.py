from application import app
from flask import Flask, jsonify, request, url_for, render_template

from uuid import uuid4
from textwrap import dedent

from .blockchain import Blockchain

node_identifier = str(uuid4()).replace('-','')

blockchain = Blockchain()

@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    return render_template('index.html',home=True)

@app.route('/mine', methods=['GET'])
def mine():

    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message' : "New Block forged!",
        'index' : block['index'],
        'transactions' : block['transactions'],
        'proof' : block['proof'],
        'previous_hash' : block['previous_hash'],
    }
    
    return render_template("mine.html",mine=True, data=response)

@app.route('/transactions/fill')
def fill_form():
    return render_template('transaction_form.html', fill_form=True)

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    
    values = request.form.to_dict()
    index = blockchain.new_transaction(values['sender'],values['recipient'],values['amount'])
    
    response = {'message': f'Transaction will added to Block {index}'}

    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain' : blockchain.chain,
        'length' : len(blockchain.chain)
    }

    return render_template("chain.html",chain=True, data=response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return 'Error : Please supply valid list of nodes', 400
    
    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message' : 'New nodes have been added',
        'total_nodes' : list(blockchain.nodes),
    }

    return jsonify(response), 201


@app.route('/consensus', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200
  