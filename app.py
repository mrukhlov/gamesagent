#!/usr/bin/env python

import os

from flask import (
	Flask,
	request,
	make_response,
	jsonify
)

app = Flask(__name__)
log = app.logger

#global guess_word
#global img_links
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

	if action == 'game.correct_guess' or action == 'game.wrong_guess':
		res = checkLetter(req)
	elif action == 'game.correct.word':
		res = correctWord(req)
	elif action == 'confirmation.yes':
		res = gameReset(req)
	elif action == 'game.start':
		res = gameStart(req)
	elif action and action.startswith('smalltalk'):
		res = smallTalk(req)
	elif action == 'slack_test':
		slack_message = {'text':'aaa', "attachments": [{"title": "IMAGE", "image_url": "https://s22.postimg.org/ih21470d9/image.png"}]}

		return make_response(jsonify({"data": {"slack": slack_message}}))
	else:
		res = None

	return make_response(jsonify(res))

def gameStart(req):

	global guess_word
	global img_links

	guess_word = ['K', '_', '_', '_', '_', 'N']
	img_links = [
		'https://s22.postimg.org/r9eee4w4d/image.png',
		'https://s22.postimg.org/z3jld9tb1/image.png',
		"https://s22.postimg.org/ih21470d9/image.png"
	]

	speech = None
	if req['result']["fulfillment"].has_key('speech'):
		speech = req["result"]["fulfillment"]['speech']

	return {
		"speech": speech,
		"displayText": speech
	}

def smallTalk(req):

	speech = None
	if req['result']["fulfillment"].has_key('speech'):
		speech = req["result"]["fulfillment"]['speech']

	return {
		"speech": speech,
		"displayText": speech
	}

def gameReset(req):

	speech = None
	if req['result']["fulfillment"].has_key('speech'):
		speech = req["result"]["fulfillment"]['speech'].replace(' _ _ _ _ ', '____')

	guess_word = ['K', '_', '_', '_', '_', 'N']

	return {
		"speech": speech,
		"displayText": speech,
		"contextOut": ['yes']
	}

def checkLetter(req):

	speech = None
	if req['result']["fulfillment"].has_key('speech'):
		speech = req["result"]["fulfillment"]['speech']

	attachments = []

	letter = req['result']['resolvedQuery'].upper()
	letter_index = index_getter(letter)
	letter_diff = [i for i in list('kitten'.upper()) if i not in guess_word]

	if guess_word.count('_') - 1 > -1:
		if guess_word.count(letter) == 0 and letter in letter_diff:
			for i in letter_index:
				guess_word[i] = letter
			if '_' in guess_word:
				output = "That's right! " + ''.join(guess_word) + '. Guess the next one.'

				if len(img_links) > 0:
					link = img_links[0]
					img_links.remove(link)

				slack_message = {
					'text': output, "attachments":
					[
						{"title": "IMAGE", "image_url": link}
					]
			     }
			else:
				output = 'You are so smart! Fantastic! Here is your kitten.'

				slack_message = {
					'text': output, "attachments":
					[
						{"title": "IMAGE", "image_url": "https://s22.postimg.org/ih21470d9/image.png"}
					]
			     }

				global guess_word
				global img_links
				guess_word = ['K', '_', '_', '_', '_', 'N']
		elif letter not in letter_diff and letter in guess_word:
			output = 'You have already guessed this letter. Try again.'
			slack_message = {'text': output}
		else:
			output = 'Almost there. Try again!'
			slack_message = {'text': output}

	return {
		#"speech": output,
		"displayText": output,
		"contextOut": [],
		"data": {"slack": slack_message}
	}

def correctWord(req):

	speech = None
	if req['result']["fulfillment"].has_key('speech'):
		speech = req["result"]["fulfillment"]['speech']

	slack_message = {
		'text': speech, "attachments":
		[
			{"title": "IMAGE", "image_url": "https://s22.postimg.org/ih21470d9/image.png"}
		]
     }

	guess_word = ['K', '_', '_', '_', '_', 'N']

	return {
		"speech": speech,
		"displayText": speech,
		"contextOut": [],
		"data": {"slack": slack_message}
	}

if __name__ == '__main__':
	port = int(os.getenv('PORT', 5000))

	app.run(
		debug=True,
		port=port,
		host='0.0.0.0'
	)