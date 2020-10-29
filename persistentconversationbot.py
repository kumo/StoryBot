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

    story_keyboard = [[story] for story in stories]
    story_markup = ReplyKeyboardMarkup(story_keyboard, one_time_keyboard=True)

    update.message.reply_text(reply_text, reply_markup=story_markup)

    #print(update.effective_chat.id)

    if 'page' in context.user_data:
        del context.user_data['page']
    if 'story' in context.user_data:
        del context.user_data['story']


def get_page_name_from_choice(page, link):
    page_name = ""
    for option in page['options']:
        if option['text'] == link:
            page_name = option['page']
            break;

    assert(page_name != "")
    return page_name


def end_story(update, context, ending):
    if 'page' in context.user_data:
        del context.user_data['page']
    if 'story' in context.user_data:
        del context.user_data['story']

    if ending == 'won':
        ending_message = "Well done! Until next time!"

    if ending == 'death':
        ending_message = "Better luck next time I hope!"

    # Create a list of buttons with only a 'Done' button
    reply_keyboard = [
        ['Done'],
    ]

    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    # Show the description with the done button
    update.message.reply_text(ending_message, reply_markup=markup, parse_mode='Markdown')


def parse_message(update, context):
    text = update.message.text

    # Is the user currently reading a story?
    if 'story' in context.user_data:
        story_name = context.user_data['story']
        story = stories[story_name]

        # Get the starting page
        previous_page_name = context.user_data['page']
        previous_page = story[previous_page_name]

        # Get the next page to read based on the option for the previous page
        page_name = get_page_name_from_choice(previous_page, text)
    else:
        # If we don't have a story, the user must have just chosen one.
        # The user's message contains the name of the story
        story = stories[text]
        # Store the name of the story for the user
        context.user_data['story'] = text

        # The story begins at the "start" page.
        page_name = 'start'

    # Get the page and remember it
    page = story[page_name]
    context.user_data['page'] = page_name

    # Get the description from the page
    reply_text = page['description']

    # Is this an ending page?
    if 'ending' in page:
        update.message.reply_text(reply_text)

        end_story(update, context, page['ending'])
        return

    # Does the page have any options?
    if 'options' in page.keys():
        # Get the list of options from the page.
        # We only want to show the text.
        actions_keyboard = [[action['text']] for action in page['options']]
        markup = ReplyKeyboardMarkup(actions_keyboard, one_time_keyboard=True)

        # Show the description with the list of buttons
        update.message.reply_text(reply_text, reply_markup=markup, parse_mode='Markdown')


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

    dp.add_handler(MessageHandler(Filters.regex('^Done$'), start))

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
