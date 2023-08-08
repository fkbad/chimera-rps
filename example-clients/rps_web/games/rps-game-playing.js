import {createTable}  from './rps_table.js';

// global queue for all sent messages 
// stores sent client requests via their id and associates
// a callback function to be run when the server
// responds to this message
//
//    sent_message_queue[request_message_id] = function_to_handle_server_response(response)
//
let sent_message_queue = {}

// increasing counter for sent out message ID's
// this + the created client ID should form a unique id per message
// across users
let next_message_id = 0

// variable to store this client's match id, if there is any
// should get filled in by the create_match/join_match callback function
// upon the successful creation/joining of a match
let MATCH_ID = null

// client_id to be used for all messages
// generated once DOM content is loaded 
// used in conjunction with the `next_message_id`
// to determine the "id" parameter of any sent message
let client_id = null

function send_message(message,websocket,callback_function) {
  /** takes a fully formatted, non-jsoned message
   * and sends it to the websocket 
   *
   * standardized through helper function to I can unify debugging statements
   *
   * Inputs:
   *     message: the actual message to send to the server
   *              does not have a fully filled in message id, 
   *              should lack the message_id sequence number
   *     
   *     websocket: the websocket to send the message to
   *
   *     callback_function: 
   *         function to be called on the servers response
   *         should only ever take in one argument: the whole server's message as a JSON object
   *              */

  const stringified_message_id = String(next_message_id)
  const message_id_to_append = client_id + "-" + stringified_message_id
  message["id"] = message_id_to_append
  next_message_id += 1

  // make sure callback_function is actually a function
  let is_func = typeof(callback_function) == "function"
  if (!is_func) {
    console.log("fed callback_function :", callback_function, "that was NOT A FUNCTION")
    return
  }

  // add message to queue with callback function
  sent_message_queue[message.id] = callback_function

  console.log("sending >>> ",message)
  websocket.send(JSON.stringify(message));
}

function parse_response(response,websocket) {
  /** function to take in any kind of response and handle it 
   * Inputs:
   *     client_id: the id of the client that sent the original message
   *     response: javascript object received from the server
   *     websocket: the websocket this client is connected on 
   *
   * Outputs:
   *     nothing, on successful parsing calls the callback function
   *              associated with the received message
   * */

  const response_has_id = response.hasOwnProperty("id")
  if (!response_has_id) {
    console.log("received response with no ID:",response)
    return
  }

  // if there is an id, then lets grab and use it!
  const response_id = response.id
  console.log("received RESPONSE from server with id", response_id);

  // make sure we actually have a response id and a return function
  // https://stackoverflow.com/questions/13417000/synchronous-request-with-websockets
  queue_callback_function = sent_message_queue[response_id]
  if (typeof(queue_callback_function) == 'function'){

    let response_function = sent_message_queue[response_id];
    response_function(response);

    // after the response function for a sent request is called, this message
    // has finished processing. thus we can delete this entry from the queue
    // to avoid memory problems
    delete sent_message_queue[response_id]
    
  } else {
    console.log("failed to find function associated with response_id")
  }
  
}

// MESSAGE CALLBACK HANDLER FUNCTIONS
// all of the following functions must take in only one parameter,
// the json string response recieved from the server
function handle_create_match(response) {
  /*
   * recieves a response to the create-match operation
   * 
   * stores the match-id returned
   */
  response = JSON.parse(response)

  // TODO validate json more here

  // the important part of a reponse is that it either 
  // has a "result" field containing the information about the successfully
  // fulfilled request, or an "error" field 
  let has_error = response.hasOwnProperty("error")
  let has_result = response.hasOwnProperty("result")

  if (!has_error && !has_result) {
    console.log("recieved response to create_match that doesn't have an error nor result:",response)
    return
  } else if (has_error && has_result) {
    console.log("recieved response to create_match that had error AND response:",response)
    return
  } 

  // guarenteed to have either an error or result at this point
  if (has_error) {
    let error = response.error
    console.log("RCVD error:",error)
    return
  } else if (has_result) {
    // successfully created match
    let result = response.result

    let has_match_id = result.hasOwnProperty("match-id")

    if (!has_match_id) {
      console.log("recieved successful create-match response without a match-id",result)
      return
    }

    // FUNCTION BODY HERE
    // record the match_id 
    MATCH_ID = result["match-id"]
    

    //
    return

  } else {
      // this syntax raises an error in the console with location in code
      throw new Error("literally should never get here")
  }
}

// HELPER FUNCTIONS

function getWebSocketServer() {
  if (window.location.host === "fkbad.github.io") {
    return "wss://sylv-connect4-ba23863cf42a.herokuapp.com/";
  } else if (window.location.host === "localhost:8000") {
    return "ws://127.0.0.1:14200";
  } else {
    throw new Error(`Unsupported host: ${window.location.host}`);
  }
}

function showMessage(message) {
  // waits 50 ms before calling the alert
  // to make sure playMove() has finished running 
  // before ending
  window.setTimeout(() => window.alert(message), 50);
}

function generate_user_id() {
  // generate the id for the user
  const location = window.location

  const hostname = location.hostname
  const port = location.port

  // https://stackoverflow.com/a/68470365
  const random_string = (len, chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') => [...Array(len)].map(() => chars.charAt(Math.floor(Math.random() * chars.length))).join('')
  const salt = random_string(5)

  const id = hostname + "-" + port + "-" + salt 

  return id
}

function updateClipboard(newClip) {
  /** takes some text and write it to clipboard */
  navigator.clipboard.writeText(newClip).then(
    () => {
      /* clipboard successfully set */
      console.log("shoulda copied [",newClip,"] to clipboard")
    },
    () => {
      /* clipboard write failed */
      console.log("couldn't write",newClip,"] to clipboard")
    },
  );
}

function create_message_for_game_move(player_move_string,client_id) {
  /*
   * creates a game-action request message in Chimera
   * format from the move a player wants to perform
   *
   * type : request
   * operation : game_action
   * id : client_id ONLY, as the `send_message()` function adds the 
   *      sequence number 
   * params: {
   *    match-id : 
   *    action : "move"
   *    data : {
   *        "move": "rock"
   *    }
   * }
   */
  // general part of message
  message = {};
  message.type = "request";
  message.operation = "game-action";

  // incomplete id, as the sequence number is appended 
  // when `send_message()` is called
  message.id = client_id;

  // fill in params
  params = {};
  params["match-id"] = "GOTTA ADD THE MATCH ID";
  params.action = "move"
  
  // fill in params data
  data = {}
  data.move = player_move_string

  params.data = data

  message.params = params

  return message

}




// BOOTSTRAP EVENT LISTENERS

function registerTable(table,websocket) {
  /* function to take in a table, and add any event listeners I want
   * at least will be on click to send messages
   */

  // Add an event listener to the table div that listens to when any of the buttons are clicked
  table.addEventListener("click", function(event) {
    // Check if the event target is a button element
    if (event.target.tagName == "BUTTON") {
      // Get the word associated with the button
      let word = event.target.innerText;
      // Assume that this function returns an object with some properties
      let message = create_message_for_game_move(word);

      // Add a new field to the message object with key "NEW_FIELD" and value "NEW_VALUE"
      message.NEW_FIELD = "NEW_VALUE";
      // Do something with the modified message object, such as sending it to the server or displaying it on the screen
      // For example:
      console.log(message);
    }
  });

}
function initGame(websocket) {

  // function to start a game upon the initialization of a websocket
  websocket.addEventListener("open", () => {

    // this returns a dictionary
    const url_params = new URLSearchParams(window.location.search)

    // search params uses dict-like get syntax
    // has separate method to check whether or not a field is in the URL

    // const match_id = url_params.get("match-id")
    const join_match_id = url_params.get("join")
    const spectate_match_id = url_params.get("spectate")

    if (join_match_id && spectate_match_id) {
      console.log('found both join and spectate match id in URI, exiting')
      return
    }


    // base message 
    let message = {
      "type": "request",
    }

    // create callback_function variable
    // to be filled in depending on what message I want to send
    let callback_function = null 


    // JOINING MATCH
    if (join_match_id) {
      // added creator tag for user creating the match
      console.log("found JOIN match id[", join_match_id, "]in URL ")
      message.operation = "join-match"
      const params = {
        // TODO remove these once we've updated chimera to 
        // not need a game parameter for Join and Create match
        "game": "rockpaperscissors",
        "match-id" : join_match_id,
        "player-name" : "player2"
      }
      message.params = params


    // SPECTATING MATCH
    } else if (spectate_match_id) {
      // spectating match
      message.operation = "spectate-match"
      const params = {
        // TODO remove these once we've updated chimera to 
        // not need a game parameter for Join and Create match
        "game": "rockpaperscissors",
        "match-id" : spectate_match_id,
        "player-name" : "player2"
      }
      message.params = params

    // CREATING MATCH
    } else  { 
      // TODO make global utils to store the information
      // about message format so message.operation = ... 
      // could be a global variable call
      message.operation = "create-match"
      const params = {
        // game ID is just the lowercase Python Class name
        "game" : "rockpaperscissors",
        "player-name" : "player1"
      };

      message.params = params;

      callback_function = handle_create_match
    }
    send_message(message,websocket,callback_function)
  });
}

function listen(websocket) {
  /** listen to any incoming message and parse it **/
  websocket.addEventListener("message", ({ data }) => {
    // receive message from the server
    const message = JSON.parse(data);
    switch (message.type) {
      case "request":
        showMessage("server sent request to user, this is fucked up <<<", message);
        break;

      case "notification":
        console.log("received notification <<<",message)
        break;

      case "response":
        console.log("received response <<<",message)
        parse_response(message,websocket)
        break;

      default:
        throw new Error(`Unsupported event type: ${message.type}.`);
    }
  });
}


// overall initializer, the bootstrap or "main"
window.addEventListener("DOMContentLoaded", () => {

  // Initialize the UI.
  const table = document.querySelector(".table");
  createTable(table)

  const websocket_address = getWebSocketServer()
  const websocket = new WebSocket(websocket_address);


  // GLOBAL VARIABLE ASSIGNMENT
  client_id = generate_user_id()

  // add event listeners to table to listen for clicks


  // listening for someone opening a websocket
  initGame(websocket)

  // listen for messages
  listen(websocket)

});
