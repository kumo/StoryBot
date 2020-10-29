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

CHOOSING_STORY, CHOOSING_ACTION = range(2)

stories = {}

def start(update, context):
    reply_text = "Hi! My name is the story teller."

    story_keyboard = [[story] for story in stories]
    story_markup = ReplyKeyboardMarkup(story_keyboard, one_time_keyboard=True)

    update.message.reply_text(reply_text, reply_markup=story_markup)

    return CHOOSING_STORY


def choose_story(update, context):
    text = update.message.text
    
    # Keep track of the story
    context.user_data['story'] = text
    # And begin the story from the start
    context.user_data['page'] = 'start'
    
    update.message.reply_text("You have chosen {}.".format(text))

    current_page = stories[text]['start']

    # Get the description from the page
    reply_text = current_page['description']

    # Get the list of options from the page.
    # We only want to show the text.
    actions_keyboard = [[action['text']] for action in current_page['options']]
    markup = ReplyKeyboardMarkup(actions_keyboard, one_time_keyboard=True)

    # Show the description with the list of buttons
    update.message.reply_text(reply_text, reply_markup=markup, parse_mode='Markdown')

    # Change the state so that we can interact with the story
    return CHOOSING_ACTION


def choose_action(update, context):
    text = update.message.text
    
    # What page did we come from?
    story = stories[context.user_data.get('story')]
    previous_page = story[context.user_data.get('page')]

    current_page_name = ""
    for option in previous_page['options']:
        if option['text'] == text:
            current_page_name = option['page']
            break;

    # Store the current page 
    context.user_data['page'] = current_page_name
    
    # Get the current page from the story
    current_page = story[current_page_name]

    # Get the description from the page
    reply_text = current_page['description']

    # Does the page have any options?
    if 'options' in current_page.keys():
        # Get the list of options from the page.
        # We only want to show the text.
        actions_keyboard = [[action['text']] for action in current_page['options']]
        markup = ReplyKeyboardMarkup(actions_keyboard, one_time_keyboard=True)

        # Show the description with the list of buttons
        update.message.reply_text(reply_text, reply_markup=markup, parse_mode='Markdown')

        # Keep the state so that we can interact with the story
        return CHOOSING_ACTION
    else:
        # Create a list of buttons with only a 'Done' button
        reply_keyboard = [
            ['Done'],
        ]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        # Show the description with the done button
        update.message.reply_text(reply_text, reply_markup=markup, parse_mode='Markdown')

        if 'ending' in current_page:
            context.user_data['ending'] = current_page['ending']

        # The player should go back to the start
        return CHOOSING_STORY


def done(update, context):
    if 'page' in context.user_data:
        del context.user_data['page']
    if 'story' in context.user_data:
        del context.user_data['story']

    if 'ending' in context.user_data:
        if context.user_data['ending'] == 'won':
            update.message.reply_text("Well done! Until next time!")

        if context.user_data['ending'] == 'death':
            update.message.reply_text("Better luck next time I hope!")

        del context.user_data['ending']
    else:
        update.message.reply_text('See you soon.')

    return ConversationHandler.END


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

    # Add conversation handler with the states CHOOSING and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_STORY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), choose_story,
                )
            ],
            CHOOSING_ACTION: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    choose_action,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
        name="my_conversation",
    )

    dp.add_handler(conv_handler)

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
