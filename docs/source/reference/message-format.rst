Message Format
==============

The Chimera message format is inspired by `JSON-RPC 2.0 <https://www.jsonrpc.org/specification>`_

A message is a `JSON <http://www.json.org/>`_ object. For example:

.. code-block::

   {
       "type": "request",
       "operation": "create-match",
       "id": "linux1.cs.uchicago.edu:54793-00001246",
       "params":
       {
           "game": "tictactoe",
           "player-name": "Alex"
       }
   }


Message Types
-------------

There are three types of messages:


* **Requests**\ : A request that the Chimera server perform a certain operation.
* **Responses**\ : A response to a request message.
* **Notifications**\ : A notification from the server to one or more clients that there has been a change in the state of the server (typically a change in the state of a particular game)

A message must have a ``"type"`` member specifying the type of the message: ``"request"``\ , ``"response"``\ , or ``"notification"``. 

Requests
^^^^^^^^

Request messages must have the following members:


* ``"type"``\ : Set to ``"request"``
* ``"operation"``\ : The operation being requested (see below for valid values)
* `"id"`: A unique identifier for this request (within the context of a single connection). We recommend using a string of the form ``"<hostname>:<port>-<sequence number>"`` (e.g., ``"linux1.cs.uchicago.edu:54793-00001246"``\ )
* ``"params"``\ : An object containing the parameters to the operation (see below for valid values). This member may be omitted.

For example:

.. code-block::

   {
       "type": "request",
       "operation": "create-match",
       "id": "linux1.cs.uchicago.edu:54793-00001246",
       "params":
       {
           "game": "tictactoe",
           "player-name": "Alex"
       }
   }



The supported operations, and their parameters, are the following:

.. list-table::
   :header-rows: 1

   * - Operation
     - Description
     - Parameters
   * - ``"list-games"``
     - List the games available in the server
     - None
   * - ``"create-match"``
     - Create a new match
     - ``"game"``\ , ``"player-name"``
   * - ``"join-match"``
     - Join an existing match as a player
     - ``"game"``\ , ``"match-id"``\ , ``"player-name"``
   * - ``"spectate-match"``
     - Join an existing match as a spectator
     - ``"game"``\ , ``"match-id"``\ , ``"spectator-name"``
   * - ``"game-action"``
     - Request a game-specific action
     - ``"match-id"``\ , ``"action"``\ , ``"data"``


See `Operations <#operations>`_ below for more details on each operation.

Responses
^^^^^^^^^

Response messages must have the following members:


* ``"type"``\ : Set to ``"response"``
* One of the following:

  * ``"result"``\ : When a request is successful, this member contains an object with the result of the request (the contents of this object will depend on the operation being performed; see `Operations <#operations>`_ for more details)
  * ``"error"``\ : When a request fails, this member contains information about the error (see `Error Object <#error-object>`_ for more details)

* ``"id"``\ : Contains the same value as the ``"id"`` member of the request object that we are responding to. If the ``"id"`` of the request cannot be established, the response will set this value to ``null``. 

For example:

.. code-block::

   {
       "type": "response",
       "id": "linux1.cs.uchicago.edu:54793-00001246",
       "result":
       {
           "match-id": "magnificent-platypus"              
       }
   }



Error object
~~~~~~~~~~~~

If a request is unsuccessful, the response will include an ``"error"`` member containing an object with the following members:


* ``"code"``\ : A numeric code for the error.
* ``"message"``\ : A string with a brief, concise error message.
* ``"data"``\ : An object containing additional data about the error. A more detailed error description may be included in a ``"details"`` member. 

The following error codes may be returned for any message. Each operation may define additional error codes.

.. list-table::
   :header-rows: 1

   * - Code
     - Message
     - Meaning
   * - -32700
     - Parse error
     - Invalid JSON was received by the server.
   * - -32600
     - Incorrect request
     - The JSON sent is not a correct Request object.
   * - -32601
     - No such operation
     - The requested operation does not exist
   * - -32602
     - Incorrect parameters
     - A parameter is incorrect or missing


Notifications
^^^^^^^^^^^^^

Notification messages must have the following members:


* ``"type"``\ : Set to ``"notification"``
* ``"scope"``\ : The scope of the notification. 
* ``"event"``\ : The event that is being notified (valid values will depend on the scope)
* ``"data"``\ : An object containing the data related to the notification.

Currently, only the ``"match"`` scope is supported (i.e., notifications related to a specific match). This scope has three possible events:


* ``"start"``\ : The match has started.
* ``"update"``\ : The state of the match has changed.
* ``"end"``\ : The match has ended.

The ``"data"`` object will have the following members:


* ``"match-id"``\ : A match identifier (see ``"create-match"`` and ``"join-match"`` below for more details).
* `"match-status"`: The status of the match: 

  * ``"awaiting-players"``\ : The match is still waiting for enough players to join.
  * ``"ready"``\ : Enough players have joined that match, and it is ready to start.
  * ``"in-progress``\ : The match is in progress.
  * ``"done"``\ : The match has concluded.

* ``"match-winner"``\ : The winner of the match. This member is only present if ``"match-status"`` is ``"done"``.
* ``"game-id"``\ : The game identifier (see ``"create-match"`` and ``"join-match"`` below for more details).
* ``"game-state"``\ : Game-specific data, as returned by the game's logic module. This member is only present if ``"match-status"`` is ``"in-progress"`` or ``"done"``.

For example:

.. code-block::

   {
       "type": "notification",
       "scope": "match",
       "event": "update",
       "data":
         {
           "match-id": "magnificent-platypus",
           "match-status": "in-progress",
           "game-id": "tictatoe",
           "game-state":
             {
               "X": "Alex",
               "O": "Sam",
               "turn": "X",
               "board": [[" ", " ", "X"],
                         [" ", "O", "X"],
                         [" ", " ", "O"]]
             }
         }
   }


Operations
----------

List games
^^^^^^^^^^

The ``"list-games"`` operation returns the list of games supported by the server. The request takes no parameters (the ``"params"`` can be omitted; if included, it must contain the empty object ``{}``\ )

For example:

.. code-block::

   {
       "type": "request",
       "operation": "list-games",
       "id": "linux1.cs.uchicago.edu:54793-00001246"
   }


On success, the ``"result"`` objects contains a single ``"games"`` member, containing an array of objects, one per game supported in the server. Each object has two members: ``"id"``\ , a string identifier for the game which can be used to refer to the game in other requests, and ``"description"``\ , a human-readable description.

For example:

.. code-block::

   { 
       "type": "response",
       "id": "linux1.cs.uchicago.edu:54793-00001246",
       "result": 
           {
               "games": [
                   {
                       "id": "rps",
                       "description": "Rock-Paper-Scissors"
                   },
                   {
                       "id": "tictactoe",
                       "description": "Tic-Tac-Toe"
                   }                    
           }
   }


There are no operation-specific error codes.

Create a new match
------------------

The ``"create-match"`` operation creates a new match of a specified game. The client must not already be participating in another match (i.e., clients are limited to participate in one match at a time).

The operation has two parameters:


* ``"game"``\ : A game identifier (as returned by the ``"list-games"`` operation)
* ``"player-name"``\ : The player name that will be associated with this client

For example:

.. code-block::

   { 
       "type": "request",
       "operation": "create-match",
       "id": "linux1.cs.uchicago.edu:54793-00001246",
       "params": 
           {
               "game": "tictactoe",
               "player-name": "Alex"
           }
   }


On success, the ``"result"`` object will contain a single ``"match-id"`` member containing a string identifier for the match that was just created. This identifier can be shared with other players who want to join or spectate.

.. code-block::

   { 
       "type": "response",
       "id": "linux1.cs.uchicago.edu:54793-00001246",
       "result": 
           {
               "match-id": "magnificent-platypus"
           }
   }


On failure, one of the following error codes will be returned:

.. list-table::
   :header-rows: 1

   * - Code
     - Message
     - Meaning
   * - -40100
     - Unknown game
     - The ``"game"`` parameter did not specify a valid game
   * - -40101
     - Already in a match
     - The client is already in another match.


Join a match
------------

The ``"join-match"`` operation allows a client to join a match as a player. The match must not have already begun (i.e., it must still be waiting for all the players to join), and the client must not already be participating in another match (i.e., clients are limited to participate in one match at a time).

The operation has three parameters:


* ``"game"``\ : A game identifier (as returned by the ``"list-games"`` operation)
* ``"match-id"``\ : A match identifier, as returned by ``"create-match"``.
* ``"player-name"``\ : The player name that will be associated with this client. This name must be unique within the match (i.e., the player name must not be the same as the name of any player that has already joined the game)

Note that, strictly speaking, the ``"game"`` parameter is redundant (since the server will know what game is associated with a valid match identifier). However, requiring the client to provide the game identifier ensures that the client is joining a game it will know how to process.

For example:

.. code-block::

   { 
       "type": "request",
       "operation": "join-match",
       "id": "linux1.cs.uchicago.edu:54793-00001246",
       "params": 
           {
               "game": "tictactoe",
               "match-id": "magnificent-platypus",
               "player-name": "Sam"
           }
   }


On success, the ``"result"`` object will be empty. For example:

.. code-block::

   { 
       "type": "response",
       "id": "linux1.cs.uchicago.edu:54793-00001246",
       "result": {}
   }


On failure, one of the following error codes will be returned:

.. list-table::
   :header-rows: 1

   * - Code
     - Message
     - Meaning
   * - -40101
     - Already in a match
     - The client is already in another match.
   * - -40102
     - Unknown match
     - The ``"match-id"`` parameter did not specify a valid match. This includes sending an incorrect ``"game"`` for the match.
   * - -40103
     - Duplicate player name
     - Another player with the same name already exists in the match


Spectate a match
----------------

The ``"spectate-match"`` operation allows a client to join a match as a spectator. If successful, the client will begin to receive notification messages for the specified match.

The operation has three parameters:


* ``"game"``\ : A game identifier (as returned by the ``"list-games"`` operation)
* ``"match-id"``\ : A match identifier, as returned by ``"create-match"``.
* ``"spectator-name"``\ : A display name associated with the spectator. May be set to ``null``.

Note that, strictly speaking, the ``"game"`` parameter is redundant (since the server will know what game is associated with a valid match identifier). However, requiring the client to provide the game identifier ensures that the client is joining a game it will know how to process.

For example:

.. code-block::

   { 
       "type": "request",
       "operation": "spectate-match",
       "id": "linux1.cs.uchicago.edu:54793-00001246",
       "params": 
           {
               "game": "tictactoe",
               "match-id": "magnificent-platypus",
               "spectator-name": null
           }
   }


On success, the ``"result"`` object will be empty. For example:

.. code-block::

   { 
       "type": "response",
       "id": "linux1.cs.uchicago.edu:54793-00001246",
       "result": {}
   }


On failure, one of the following error codes will be returned:

.. list-table::
   :header-rows: 1

   * - Code
     - Message
     - Meaning
   * - -40102
     - Unknown match
     - The ``"match-id"`` parameter did not specify a valid match. This includes sending an incorrect ``"game"`` for the match.


Game-specific actions
---------------------

The ``"game-action"`` operation allows a client to send an action to a game (e.g., making a move).

The operation has three parameters:


* ``"match-id"``\ : A match identifier, as returned by ``"create-match"``.
* ``"action"``\ : The action to perform. The list of acceptable actions will be specific to each game (i.e., you should consult the documentation for the game for a list of valid actions).
* ``"data"``\ : A JSON object containing action-specific data. Like the previous parameter, the acceptable values for this parameter will be specific to each game.

For example:

.. code-block::

   { 
       "type": "request",
       "operation": "game-action",
       "id": "linux1.cs.uchicago.edu:54793-00001246",
       "params": 
           {
               "match-id": "magnificent-platypus",
               "action": "move",
               "data": {"position": [0,0]}
           }
   }


On success, the ``"result"`` object contain game-specific result data.

For example:

.. code-block::

   { 
       "type": "response",
       "id": "linux1.cs.uchicago.edu:54793-00001246",
       "result": 
         {
           "updated": 
           {
             "position": [0,0],
             "value": "X"
           }
         }
   }


On failure, one of the following error codes will be returned:

.. list-table::
   :header-rows: 1

   * - Code
     - Message
     - Meaning
   * - -40105
     - Incorrect match
     - The ``"match-id"`` parameter does not contain the player's match (or the player is not in a match at all)
   * - -50100
     - Action not allowed outside player's turn
     - The player requested an action that is only allowed during the player's turn
   * - -50101
     - Unsupported action in game
     - The ``"action"`` parameter specified an action that is not supported by the game
   * - -50102
     - Incorrect data in game action
     - The game rejected the contents of the ``"data"`` parameter.
   * - -50103
     - Incorrect move
     - The player attempted a move that is not valid

