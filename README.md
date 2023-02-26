# Chimera

Chimera is a framework for publishing games through a [websockets](https://en.wikipedia.org/wiki/WebSocket)-based API, allowing users to play games remotely through a variety of interfaces (web, mobile, desktop, etc.). It was developed at the [University of Chicago's Department of Computer Science](https://www.cs.uchicago.edu/) to support course projects, allowing students to explore topics in software design, APIs, networked applications, etc.

## Installing

Chimera is not yet available as an installable package. To try out Chimera, clone this
repository and create a virtual environment as follows:

    python3 -m venv venv
    source venv/bin/activate
    pip3 install -e .

## Running

Chimera includes an implementation of Connect-M (a general form of Connect Four)
that you can use to familiarize yourself with Chimera. Before trying out this
example, make sure to install the dependencies needed to run the example
clients:

    pip3 install -e .[example_clients]

Next, open three terminals, making sure to activate the virtual environment
in all of them. In the first terminal run this:

    chimera-server --load-game chimera.examples.connectm.ConnectM --log-level DEBUG

You should see something like this:

    2023-02-26 11:02:42,728 chimera.server INFO Server listening on 127.0.0.1:14200

In the second terminal, run this:

    python3 example-clients/connectm/tui.py

This command will run a terminal-based interface for Connect Four. Before doing
so, it will create a match in the Chimera server, and will wait for another
player to join. You should see something like this:

    Your match ID is fabulous-capybara
    Waiting for other player to join...

The match ID above is an example; you will get a unique match ID when you run the command.

In the third terminal, run this:

    python3 example-clients/connectm/bot.py <MATCH-ID>

Make sure to replace `<MATCH-ID>` with the match ID you received in the second terminal.
This will run a simple game-playing bot that will just make moves at random.
It will first connect to the Chimera server, and will join the match you
created in the second terminal. You should see this:

    It is <USER>'s turn. Waiting for their move...

(you should see your username in place of `<USER>`)

Now, if you go back to the second terminal, the game will have begun, and you
will be able to start playing:


    ┌─┬─┬─┬─┬─┬─┬─┐
    │ │ │ │ │ │ │ │
    ├─┼─┼─┼─┼─┼─┼─┤
    │ │ │ │ │ │ │ │
    ├─┼─┼─┼─┼─┼─┼─┤
    │ │ │ │ │ │ │ │
    ├─┼─┼─┼─┼─┼─┼─┤
    │ │ │ │ │ │ │ │
    ├─┼─┼─┼─┼─┼─┼─┤
    │ │ │ │ │ │ │ │
    ├─┼─┼─┼─┼─┼─┼─┤
    │ │ │ │ │ │ │ │
    └─┴─┴─┴─┴─┴─┴─┘
    
    borja> 

Just enter a number between 1 and 7, and press Enter, to make a move.

As you play the game, you will be able to see the messages that are being sent
between the clients and server in the first terminal.

You can also try running through the above steps, but doing the following:

- In the third terminal, run another text-based client like this:

      python3 example-clients/connectm/tui.py --join-match <MATCH-ID>

  If you have the terminals side by side, you can make moves in each, 
  and see how the game advances from the perspective of each player.
 
- In the third terminal, run a GUI like this:

      python3 example-clients/connectm/gui.py --join-match <MATCH-ID>

- Try doing any of the above, but running the server on one computer, and
  the clients in a different computer. By default, the clients connect to 
  a server running on `localhost`, but you can specify the address of
  the server with the `--chimera-server` argument to the clients.
  For example:
  
      python3 example-clients/connectm/tui.py --chimera-server ws://example.org:14200

  The server listens on port 14200 by default, but you can adjust this
  with the `--addr-port` argument:

      chimera-server --load-game chimera.examples.connectm.ConnectM --log-level DEBUG --addrport 0.0.0.0:14300  
