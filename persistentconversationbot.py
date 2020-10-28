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
    PicklePersistence,
)

import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING_STORY, CHOOSING_ACTION = range(2)

story = {'title': 'The house that killed Sam', 'start': {'title': 'The House', 'description': 'You are in a house. A familiar house, but it is dark.', 'options': [{'text': 'Turn on the light', 'page': 'death-by-light'}, {'text': "Don't turn on the light", 'page': 'death-by-darkness'}, {'text': 'Offer food', 'page': 'offer-food'}]}, 'death-by-light': {'description': 'You turn on the light, and seen the mighty Nuala.  She casts her gaze upon you, freezing your blood, and then, with a whisk of her tail, chops off your head.', 'death': True}, 'death-by-darkness': {'description': 'You leave the light off; better safe than sorry.  A rumbling sound starts to form next to you; A rhythmic purring sound, that grows louder and louder.  You begin to shake, your brain begins to shake, and your life begins to shake, until it breaks.', 'death': True}, 'offer-food': {'description': 'You stumble around in the dark, reaching for a tin of cat food. You find one and pull it open, cutting yourself in the process. As you search for a bowl you hear a licking sound, surely cleaning up your blood drops, ever getting closer, ever getting closer. With great haste you prepare the food and place it on the floor. The licking turns to crunching, before fading away. Leaving you, alone in the house, in the dark.', 'end': True}}


def start(update, context):
    reply_text = "Hi! My name is the story teller."

    reply_keyboard = [
        ['The House that Killed Sam'],
        ['Done'],
    ]
    story_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    update.message.reply_text(reply_text, reply_markup=story_markup)

    return CHOOSING_STORY


def choose_story(update, context):
    text = update.message.text
    
    # Keep track of the story
    context.user_data['story'] = text
    # And begin the story from the start
    context.user_data['page'] = 'start'
    
    update.message.reply_text("You have chosen {}.".format(text))

    current_page = story['start']

    # Get the description from the page
    reply_text = current_page['description']

    # Get the list of options from the page.
    # We only want to show the text.
    actions_keyboard = [[action['text']] for action in current_page['options']]
    markup = ReplyKeyboardMarkup(actions_keyboard, one_time_keyboard=True)

    # Show the description with the list of buttons
    update.message.reply_text(reply_text, reply_markup=markup)

    # Change the state so that we can interact with the story
    return CHOOSING_ACTION


def choose_action(update, context):
    text = update.message.text
    
    # What page did we come from?
    previous_page = story[context.user_data.get('page')]

    current_page_name = ""
    for option in previous_page['options']:
        if option['text'] == text:
            current_page_name = option['page']
            break;

    # Store the current page 
    context.user_data['page'] == current_page_name
    
    # Get the current page from the story
    current_page = story[current_page_name]

    # Get the description from the page
    reply_text = current_page['description']

    # Does the page have any options?
    if 'option' in current_page.keys():
        # Get the list of options from the page.
        # We only want to show the text.
        actions_keyboard = [[action['text']] for action in current_page['options']]
        markup = ReplyKeyboardMarkup(actions_keyboard, one_time_keyboard=True)

        # Show the description with the list of buttons
        update.message.reply_text(reply_text, reply_markup=markup)

        # Keep the state so that we can interact with the story
        return CHOOSING_ACTION
    else:
        # Create a list of buttons with only a 'Done' button
        reply_keyboard = [
            ['Done'],
        ]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        # Show the description with the done button
        update.message.reply_text(reply_text, reply_markup=markup)

        # TODO: show something that shows whether the player won or lost

        # The player should go back to the start
        return CHOOSING_STORY


def done(update, context):
    if 'page' in context.user_data:
        del context.user_data['page']
    if 'story' in context.user_data:
        del context.user_data['story']

    update.message.reply_text(
        "Until next time!"
    )
    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bot's token.
    pp = PicklePersistence(filename='conversationbot')
    updater = Updater("***REMOVED***", persistence=pp, use_context=True)

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
        persistent=True,
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
