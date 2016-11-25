#!/usr/bin/env python

'''used as webhook'''

import os

from flask import (
	Flask,
	request,
	make_response,
	jsonify
)

app = Flask(__name__)
log = app.logger

def index_getter(letter):
	index = 0
	index_list = []
	for i in 'kitten'.upper():
		if i == letter:
			index_list.append(index)
		index+=1
	return index_list

def reset_vars():

	global guess_word
	global img_links

	guess_word = ['K', '_', '_', '_', '_', 'N']
	img_links = [
		'https://s22.postimg.org/r9eee4w4d/image.png',
		'https://s22.postimg.org/z3jld9tb1/image.png',
		"https://s22.postimg.org/ih21470d9/image.png"
	]

@app.route('/webhook', methods=['POST'])
def webhook():

	req = request.get_json(silent=True, force=True)

	action = req["result"].get("action")

	if action == 'game.letter':
		res = checkLetter(req)
	elif action == 'game.word.correct':
		res = correctWord(req)
	elif action == 'confirmation.yes':
		res = gameReset(req)
	elif action == 'game.start':
		res = gameStart(req)
	elif action and action.startswith('smalltalk'):
		res = smallTalk(req)
	else:
		log.error("Unexpeted action.")

	return make_response(jsonify(res))

def gameStart(req):

	reset_vars()

	speech = req["result"]["fulfillment"].get("speech")

	return {
		"speech": speech,
		"displayText": speech
	}

def smallTalk(req):

	speech = req["result"]["fulfillment"].get("speech")

	return {
		"speech": speech,
		"displayText": speech
	}

def gameReset(req):

	speech = req["result"]["fulfillment"].get("speech").replace(' _ _ _ _ ', '____')

	reset_vars()

	return {
		"speech": speech,
		"displayText": speech,
		"contextOut": ['yes']
	}

def checkLetter(req):

	attachments = []

	letter = req['result']['resolvedQuery'].upper()
	letter_index = index_getter(letter)
	letter_diff = [i for i in list('kitten'.upper()) if i not in guess_word]

	if guess_word.count(letter) == 0 and letter in letter_diff:
		for i in letter_index:
			guess_word[i] = letter
		if '_' in guess_word:
			output = "That's right! " + ''.join(guess_word) + '. Guess the next one.'

			if len(img_links) > 0:
				link = img_links.pop(0)

			attachments.append({"title": "IMAGE", "image_url": link})
		else:
			output = 'You are so smart! Fantastic! Here is your kitten.'
			attachments.append({"title": "IMAGE", "image_url": "https://s22.postimg.org/ih21470d9/image.png"})

			reset_vars()

	elif letter in guess_word:
		output = 'You have already guessed this letter. Try again.'
	else:
		output = 'Almost there. Try again!'

	slack_message = {'text': output, "attachments":attachments}

	return {
		#"speech": output,
		"displayText": output,
		"contextOut": ['guessing'],
		"data": {"slack": slack_message}
	}

def correctWord(req):

	global guess_word

	speech = req["result"]["fulfillment"].get("speech")

	slack_message = {
		'text': speech, "attachments":
		[
			{"title": "IMAGE", "image_url": "https://s22.postimg.org/ih21470d9/image.png"}
		]
     }

	reset_vars()

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