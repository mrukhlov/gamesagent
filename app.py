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

	speech = None
	if req['result']["fulfillment"].has_key('speech'):
		speech = req["result"]["fulfillment"]['speech']

	action = None
	if req['result'].has_key('action'):
		action = req['result']['action']

	'''if action == 'game.correct_guess' or action == 'game.wrong_guess':
		res = CheckLetter(req)
	elif action == 'game.correct.word':
		res = correctWord(req)
	elif action == 'confirmation.yes':
		res = gameReset(req)
	else:
		log.error("Unexpeted action.")

	return make_response(jsonify(res))'''

	if action == 'game.correct_guess' or action == 'game.wrong_guess':
		res, picture = CheckLetter(req)
	elif action == 'game.correct.word':
		guess_word = ['K', '_', '_', '_', '_', 'N']
		res = speech
	elif action == 'confirmation.yes':
		res = speech.replace(' _ _ _ _ ', '____')
	elif action == 'game.start':
		guess_word = ['K', '_', '_', '_', '_', 'N']
		img_links = [
			'https://s22.postimg.org/r9eee4w4d/image.png',
			'https://s22.postimg.org/z3jld9tb1/image.png',
			"https://s22.postimg.org/ih21470d9/image.png"
		]
		res = speech
	elif action and action.startswith('smalltalk'):
		res = speech
	elif action == 'slack_test':
		slack_message = {'text':'aaa', "attachments": [{"title": "IMAGE", "image_url": "https://s22.postimg.org/ih21470d9/image.png"}]}
		return {"data": {"slack": {slack_message}}}
	else:
		res = None

	return res, action, picture

def gameReset(req):
	guess_word = ['K', '_', '_', '_', '_', 'N']
	output = "Cool! Let's start. The word is K _ _ _ _ N. Guess a letter! Note that every time you guess a letter, your cat is growing."

	return {
		"speech": output,
		"displayText": output,
		"contextOut": ['yes']
	}

def CheckLetter(req):

	letter = req['result']['resolvedQuery'].upper()
	letter_index = index_getter(letter)
	letter_diff = [i for i in list('kitten'.upper()) if i not in guess_word]

	picture = True

	if guess_word.count('_') - 1 > -1:
		if guess_word.count(letter) == 0 and letter in letter_diff:
			for i in letter_index:
				guess_word[i] = letter
			if '_' in guess_word:
				output = "That's right! " + ''.join(guess_word) + '. Guess the next one.'
			else:
				output = 'You are so smart! Fantastic! Here is your kitten.'
				global guess_word
				global img_links
				guess_word = ['K', '_', '_', '_', '_', 'N']
		elif letter not in letter_diff and letter in guess_word:
			output = 'You have already guessed this letter. Try again.'
			picture = False
		else:
			output = 'Almost there. Try again!'

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