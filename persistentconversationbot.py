#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)

import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

stories = {}

def start(update, context):
    reply_text = "Hi! My name is the story teller."

    # Show the user the list of available stories
    story_keyboard = [[story] for story in stories]
    story_markup = ReplyKeyboardMarkup(story_keyboard, one_time_keyboard=True)

    update.message.reply_text(reply_text, reply_markup=story_markup)

    #print(update.effective_chat.id)

    if 'story' in context.user_data:
        del context.user_data['story']
    if 'page' in context.user_data:
        del context.user_data['page']


def end_story(update, context):
    story = stories[context.user_data['story']]
    previous_page_name = context.user_data['page']
    previous_page = story[previous_page_name]	

    if previous_page['ending'] == 'won':
        ending_message = "Well done! Until next time!"

    if previous_page['ending'] == 'death':
        ending_message = "Better luck next time, I hope!"

    # Show the description with the done button
    # update.message.reply_text(ending_message, reply_markup=markup, parse_mode='Markdown')
    update.message.reply_text(ending_message, parse_mode='Markdown')

    if 'story' in context.user_data:
        del context.user_data['story']
    if 'page' in context.user_data:
        del context.user_data['page']


def start_new_story(update, context, story_name):
    # If we don't have a story, the user must have just chosen one.
    # The user's message contains the name of the story
    story = stories[story_name]
    # Store the name of the story for the user
    context.user_data['story'] = story_name


def get_next_page(update, context, page_link_text):
    story = stories[context.user_data['story']]

    # If the page is missing, just get the 'start' page
    if 'page' not in context.user_data:
        # Get the page and remember it
        page = story['start']
        context.user_data['page'] = 'start'

        return page

    previous_page_name = context.user_data['page']
    previous_page = story[previous_page_name]

    for option in previous_page['options']:
        if option['text'] == page_link_text:
            page_name = option['page']
            break;

    # Get the page and remember it
    page = story[page_name]
    context.user_data['page'] = page_name
    
    return page


def get_page_keyboard(page):
    # Does the page have any options?
    if 'options' in page.keys():
        # Get the list of options from the page.
        # We only want to show the text.
        actions_keyboard = [[action['text']] for action in page['options']]
    else:
        # Create a list of buttons with only a 'Done' button
        actions_keyboard = [
            ['Done'],
        ]

    return actions_keyboard


def parse_message(update, context):
    text = update.message.text

    # If needed, start a new story
    if 'story' not in context.user_data:
        start_new_story(update, context, text)

    page = get_next_page(update, context, text)

    # Get the description from the page
    description_text = page['description']

    actions_keyboard = get_page_keyboard(page)
    markup = ReplyKeyboardMarkup(actions_keyboard, one_time_keyboard=True)

    # Show the description with the list of buttons
    update.message.reply_text(
        description_text,
        reply_markup=markup,
        parse_mode='Markdown')


# We need to be able to create folders and list contents of folders
from os import listdir
from os.path import isfile, join

import toml

def load_stories():
    # Look for stories
    story_files = [f for f in listdir("Stories") if isfile(join("Stories", f))]

    assert(len(story_files) > 0)

    for story_file in story_files:
        story = toml.load(join("Stories", story_file))

        stories[story['title']] = story


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("***REMOVED***", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add handlers for different commands (for example /start)
    # the string is the command (without "/") and after there is the function.
    dp.add_handler(CommandHandler("start", start))

    # Add a handler for a normal message (in this case, parse_message)
    dp.add_handler(MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), parse_message))

    dp.add_handler(MessageHandler(Filters.regex('^Done$'), end_story))

    # Load the stories
    load_stories()

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
