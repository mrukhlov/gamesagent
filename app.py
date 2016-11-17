#!/usr/bin/env python

import os
import random

from flask import (
	Flask,
	request,
	make_response,
	jsonify
)

app = Flask(__name__)
log = app.logger

global guess_word
guess_word = ['K', '_', '_', '_', '_', 'N']

def index_getter(letter):
	index = 0
	index_list =[]
	for i in list('kitten'.upper()):
		if i == letter:
			index_list.append(index)
		index+=1
	return index_list

@app.route('/webhook', methods=['POST'])
def webhook():
	req = request.get_json(silent=True, force=True)

	action = req['result']['action']
	res = {'test':'test'}

	if action == 'game.correct_guess' or action == 'game.wrong_guess':
		res = CheckLetter(req)
	elif action == 'game.correct.word':
		res = correctWord(req)
	elif action == 'confirmation.yes':
		res = gameReset(req)
	else:
		log.error("Unexpeted action.")

	return make_response(jsonify(res))

def gameReset(req):
	guess_word = ['K', '_', '_', '_', '_', 'N']

def CheckLetter(req):

	letter = req['result']['resolvedQuery'].upper()
	letter_index = index_getter(letter)
	letter_diff = [i for i in list('kitten'.upper()) if i not in guess_word]

	if guess_word.count('_') - 1 > 0:
		if guess_word.count(letter) == 0 and letter in letter_diff:
			for i in letter_index:
				guess_word[i] = letter
			output = "That's right! " + ''.join(guess_word) + '. Guess the next one.'
		elif letter not in letter_diff:
			output = 'Almost there. Try again!'
		else:
			output = 'You named it already, try again. Word is ' + ''.join(guess_word)
	else:
		output = 'You are so smart! Fantastic! Here is your kitten.'

	return {
		"speech": output,
		"displayText": output,
		"contextOut": []
	}

def correctWord(req):
	output = 'You are so smart! Fantastic! Here is your kitten.'
	guess_word = ['K', '_', '_', '_', '_', 'N']
	return {
		"speech": output,
		"displayText": output,
		"contextOut": []
	}



if __name__ == '__main__':
	port = int(os.getenv('PORT', 5000))

	app.run(
		debug=True,
		port=port,
		host='0.0.0.0'
	)
