from application import app
from flask import Flask, jsonify, request, url_for, redirect, render_template, flash
from application.forms import TransactionForm, NodeRegisterForm
from uuid import uuid4
from textwrap import dedent

from .blockchain import Blockchain

node_identifier = str(uuid4()).replace('-','')

blockchain = Blockchain()


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    return render_template('index.html',home=True)

@app.route('/mine')
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


@app.route('/transactions/new', methods=['GET','POST'])
def new_transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        sender       = form.sender.data
        recipient    = form.recipient.data
        amount       = form.amount.data

        index = blockchain.new_transaction(sender,recipient,amount)
    
        response = f'Transaction will added to Block {index}'
        flash(response,"success")
        return redirect("/home")
    return render_template('transaction.html',title="New Transaction", form=form, transaction=True)


@app.route('/chain')
def full_chain():
    response = {
        'chain' : blockchain.chain,
        'length' : len(blockchain.chain)
    }

    return render_template("chain.html",chain=True, data=response), 200

 
@app.route('/nodes/register', methods=['GET','POST'])
def register_node():
    form = NodeRegisterForm()
    if form.validate_on_submit():
        node = form.node.data
        blockchain.register_node(node)
    
        response = f'New nodes have been added.\n Total nodes: {len(blockchain.nodes)}'
        flash(response,"success")
        return redirect("/home")
    return render_template('register_node.html', title="New Node Registration", form=form, new_node=True)


@app.route('/consensus')
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

    return render_template("consensus.html", data=response, consensus=True), 200
