# POC for Discord bot

```
USAGE: bot.py <command> [params]...

Available Commands
  message
	Test the connection by sending a message (param: message)
  create-role
	Create a role (param: role name)
  add-role
	Add a role to a user (params: username, rolename)
  help
	This help message
```

## Notes

- Since the bot wont have a command line interface, I didn't bother making any kind of nice argument parsing.  This is a very stupid prototype.
- Using usernames for role assignment is bad.  Usernames aren't unique, so any real application should use IDs for everything.
- There's a function and a commented line that logs the bot in to the gateway.  This is required to be done at least once to be able to send messages.  It may be necessary to keep an open websocket if we end up adding functionality that requires it.
