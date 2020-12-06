# StoryBot
A choose your own adventure Telegram bot.

This bot will read stories written in TOML format and present them to the user. A simple story follows:

```toml
title = "The house that loved Sam"

[start]
description = "You are in a house. A familiar house, but it is dark."

[[start.options]]
text = "Turn on the light"
page = "turn-on-light"

[[start.options]]
text = "Don't turn on the light"
page = "no-turn-on-light"

[[start.options]]
text = "Offer food"
page = "offer-food"

[turn-on-light]
description = "You turn on the light, and seen the mighty Nuala.  She casts her gaze upon you, warming your blood, and then, with a whisk of her tail, captures your heart."
ending = "won"

[no-turn-on-light]
description = "You leave the light off; better safe than sorry.  A rumbling sound starts to form next to you; A rhythmic purring sound, that grows louder and louder.  You begin to relax, your breathing slows, and a Nuala sleeps next to you."
ending = "won"

[offer-food]
description = "You stumble around in the dark, reaching for a tin of cat food. You find one and pull it open, dirting yourself in the process. As you search for a bowl you hear a licking sound, surely cleaning the food from your hand. With great haste you prepare the food and place it on the floor. The licking turns to crunching, before fading away, purring, forever purring. Leaving you, in the dark, wondering if you should turn the light on."
ending = "won"
```

When the user starts, they will be shown the list of stories using the `title` and when they choose a story, they will first be shown the description and then the list of options if they exist. Each option has the text to show the user and the link. If a page has an ending, then the story will end there, but depending on whether the text is `won` or `death`, the user will be shown a different message.
