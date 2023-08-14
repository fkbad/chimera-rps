import { createTable } from './rps_table.js';

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

// websocket for client connection
// global variable as it is assigned once upon page load per client 
let websocket = null

function send_message(message, websocket, callback_function) {
  /** takes a fully formatted, non-jsoned message
   * and sends it to the websocket 
   *
   * standardized through helper function to I can unify debugging statements
   *
   * Inputs:
   *     message: the actual message to send to the server
   *              message should not have an ID field, as that 
   *              will be filled in here
   *     
   *     websocket: the websocket to send the message to
   *
   *     callback_function: 
   *         function to be called on the servers response
   *         should only ever take in one argument: the whole server's message as a JSON object
   *              */

  // should never send a message before we have a client_id
  if (client_id === null) {
    console.error("tried to send message before client_id was assigned")
    return
  }

  const already_has_id = message.hasOwnProperty("id")
  if (already_has_id) {
    console.error("message giving to send_message that already had ID field", message)
    return
  }
  const stringified_message_id = String(next_message_id)

  const message_id_to_append = client_id + "-" + stringified_message_id
  message["id"] = message_id_to_append
  next_message_id += 1

  // MAYBE SHOULD BE UNCOMMENTED
  // make sure callback_function is actually a function
  // let is_func = typeof(callback_function) == "function"
  // if (!is_func) {
  //   console.error("fed callback_function :", callback_function, "that was NOT A FUNCTION")
  //   return
  // }

  // add message to queue with callback function
  sent_message_queue[message.id] = callback_function;
  //console.log("typeof send-message callback is:",typeof(callback_function));
  //console.log("send-message callback is:",callback_function);

  //console.log("typeof queue'd callback is:",typeof(sent_message_queue[message.id]));
  //console.log("queue'd callback is:",sent_message_queue[message.id]);

  console.log("sending >>> ", message)
  websocket.send(JSON.stringify(message));
}

function parse_response(response) {
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

  const [response_is_valid, response_type] = validate_response(response);

  if (response_is_valid) {
    if (response_type == "error") {
      raise_response_error(response)
    } else if (response_type == "success") {
      call_appropriate_callback(response)
    } else {
      throw new Error("validate_response said a response was valid, but did not provide a valid response type, instead gave:", response_type)
    }
    // after finishing our reponse processing by 
    // - either the response function finishing 
    // - or an error was raised in the error log
    // we then delete the item from the message queue
    // to avoid memory problems, and because there
    // is nothing left to do with this request-response cycle

    // dictionary deletes raise no errors if the 
    // key is not actually in the dictionary, 
    // so if the response id is not a key, this 
    // delete will silently do nothing
    //
    // this should never happen as validate_reseponse
    // should only deem a response valid if the response ID 
    // is in the queue
    delete sent_message_queue[response.id]
    return

  } else {
    // validate response should log the more specific error 
    // that arose during processing, and have also removed
    // entries in the queue if there was any for the ID
    // of this response, thus we are done parsing this response
    return
  }
}

// MESSAGE CALLBACK HANDLER FUNCTIONS
// all of the following functions must take in only one parameter,
// the json string response recieved from the server

function handle_join_match(response) {
  /* function to handle the successful response to 
   * joining a match
   *
   * Inputs: 
   *    response: the response object recieved from the server after sending a 
   *              join-match request
   */

  //assign match ID
  let search_params = new URLSearchParams(window.location.search);
  let match_id = search_params.get("join");
  MATCH_ID = match_id;

  console.log("successfully joined match", MATCH_ID)

  // add event listeners to table to listen for clicks
  const table = document.querySelector(".table");
  registerTable(table)
}

function handle_game_action(response) {
  /*
   * function to handle the response to a game-action
   *
   * Inputs:
   *    response: the response object recieved from the server after sending a game-action
   *
   * Outputs; 
   *    None
   */

  // update move log
  // update the board
  console.log("HANDLING GAME-ACTION RESPONSE:", response)
  const result = response.result

  const move_string = result.move;
  update_display_with_player_move(move_string)
  const move_log_item = get_move_log_item_from_result(result)

  update_move_log(move_log_item)
}
function handle_create_match(response) {
  /*
   * recieves a response to the create-match operation
   * 
   * stores the match-id returned
   */
  // TODO validate json more here

  console.log("handling create match with response:", response)

  // successfully created match
  let result = response.result

  let has_match_id = result.hasOwnProperty("match-id")

  if (!has_match_id) {
    console.error("recieved successful create-match response without a match-id", result)
    return
  }

  // FUNCTION BODY HERE
  // record the match_id 
  MATCH_ID = result["match-id"]
  console.log("MATCH ID global variable assigned to: \"", MATCH_ID, "\"")

  const table = document.querySelector(".table");

  // add event listeners to table to listen for clicks
  // ONLY after the match has successfully been created
  registerTable(table)

  // add join and spectate buttons with the appropriate links 
  // now that we have the match id
  populate_join_buttons()

  return
}

// HELPER FUNCTIONS

function update_display_with_player_move(player_move_string) {
  /* function to update the box with "Your Move" with the content of your actual move
   *
   * Inputs:
   *    player_move_string: the string corresponding to the players move
   *
   * Outputs:
   *    none
   *
   * Side Affects:
   *    adds text to the .move_box with id "player_move_box"
   */
  let player_move_box = document.getElementById("player_move_box");
  player_move_box.innerText = player_move_string;
}
function format_move_string_for_log(result) {
  /* function to take in a result from a move game-action response 
   * and return whatever text I want in the corresponding
   * move-log item
   *
   * Inputs: 
   *    result section of succesful game-action response sent from server
   *    of format:
   *    result = {
   *      "move" : move_string
   *    }
   *
   * Outputs:
   *    string: some string of to be used as the text for
   *            some error log entry
   */
  let move_string = result.move;
  let output = "Played: " + move_string
  return output

}
function get_move_log_item_from_result(result) {
  /* function to return an appropriate list item
   * for a succesful move
   * 
   * Inputs:
   *    the result section of a successful game_action response
   *
   * Ouputs:
   *    html <li> containing the desired text to display a move
   */
  let output_list_element = document.createElement("li")

  let formatted_move_text = format_move_string_for_log(result)

  output_list_element.textContent = formatted_move_text

  output_list_element.className = "move_log_list_item"

  return output_list_element
}

function update_move_log(move_log_item) {
  /* function to update the move log with a new item
   *
   * Inputs: 
   *    move_log_item : a list item <li> with whatever text is necesarry
   *                     with class "move_log_list_item"
   *
   * Outputs:
   *    nothing
   *
   * Side Effects:
   *    prepending this item to the move_log
   */
  let move_log_list = document.getElementById("move_log_list");

  console.log("trying to prepend move item:", move_log_item)

  move_log_list.append(move_log_item)
}

function populate_join_buttons() {
  /* function to create buttons that on click
   * copy the proper join and spectate links to clipboard
   *
   * buttons are added to the "match_actions" classed div
   *
   * Inputs: 
   *    none, will instead grab from the global MATCH_ID
   *    which is assigned in handle_create_match before this function is called
   *
   * Outputs:
   *    none, will instead append buttons to the match_actions div
   */
  console.log("trying to populate match buttons")
  let join_button = document.createElement("button")
  let spectate_button = document.createElement("button")

  join_button.className = "game_action_button"
  join_button.id = "copy_join_link_button"

  spectate_button.className = "game_action_button"
  spectate_button.id = "copy_spectate_link_button"

  const join_uri = get_join_link_uri()
  const spectate_uri = get_spectate_link_uri()
  // const join_uri = "TEMP JOIN URI"
  // const spectate_uri = "TEMP SPECTATE URI"

  join_button.textContent = "Copy Join Link"
  spectate_button.textContent = "Copy Spectate Link"


  // get the soon-to-parent element
  let parent = document.getElementById("match_actions")

  let buttons_and_links = {};
  buttons_and_links[join_uri] = join_button;
  buttons_and_links[spectate_uri] = spectate_button;

  // add event listeners
  // this for loop syntax gets the keys in the object
  for (let button_uri in buttons_and_links) {
    let button = buttons_and_links[button_uri]
    button.addEventListener("click", function() {
      updateClipboard(button_uri)
    });

    // add the button to the parent div
    parent.appendChild(button)
  };
}

function get_spectate_link_uri() {
  /* function to generate the spectate link for a match 
   * 
   * Inputs: 
   *    none, will call on the global MATCH_ID
   *
   * Outputs
   *    string: the full URI to spectate the match
   */

  // to construct the URI we need:
  // - base URI (localhost or whatever/games/rps.html)
  // - the game_id of the created match (in the url with ?game_id=rps or =rpsls)
  // - the MATCH_ID to give as the argument in ?spectate

  //first get game_id
  // Get the current URL object 
  const current_url = new URL(window.location.href);

  // Get the search parameters object 
  let search_params = new URLSearchParams(current_url.search);

  // extract only the game_id
  let game_id = search_params.get("game_id");
  console.log(game_id)

  // make the search params for outputting
  // empty so we can manually add the only two we want
  let output_search_params = new URLSearchParams();

  output_search_params.append("game_id", game_id)
  output_search_params.append("spectate", MATCH_ID)

  // Set the new search string to the URL object 
  // this preserves the origin and pathname
  // of the current_url while changing the search parameters
  current_url.search = output_search_params.toString();

  // Get the new URI as a string 
  const spectate_uri = current_url.toString();
  console.log("made spectate link:", spectate_uri);

  return spectate_uri



}
function get_join_link_uri() {
  /* function to generate the join link for a match 
   * 
   * Inputs: 
   *    none, will call on the global MATCH_ID
   *
   * Outputs
   *    string: the full URI to join the match
   */

  // to construct the URI we need:
  // - base URI (localhost or whatever/games/rps.html)
  // - the game_id of the created match (in the url with ?game_id=rps or =rpsls)
  // - the MATCH_ID to give as the argument in ?join

  //first get game_id
  // Get the current URL object 
  const current_url = new URL(window.location.href);

  // Get the search parameters object 
  let search_params = new URLSearchParams(current_url.search);

  // extract only the game_id
  let game_id = search_params.get("game_id");
  console.log(game_id)

  // make the search params for outputting
  // empty so we can manually add the only two we want
  let output_search_params = new URLSearchParams();

  output_search_params.append("game_id", game_id)
  output_search_params.append("join", MATCH_ID)

  // Set the new search string to the URL object 
  // this preserves the origin and pathname
  // of the current_url while changing the search parameters
  current_url.search = output_search_params.toString();

  // Get the new URI as a string 
  const join_uri = current_url.toString();
  console.log("made join link:", join_uri);

  return join_uri



}
function raise_response_error(response) {
  /*
   * function to take in an error response
   * and update the error log
   */
  console.log("trying to update error log with response:", response)
  const error = response.error

  const error_log_item = get_error_log_item_from_error(error)

  update_error_log(error_log_item)
}

function update_error_log(error_log_item) {
  /* function to update the error log with a new item
   *
   * Inputs: 
   *    error_log_item : a list item <li> with whatever text is necesarry
   *                     with class "error_log_list_item"
   *
   * Outputs:
   *    nothing
   *
   * Side Effects:
   *    prepending this item to the error_log
   */
  let error_log_list = document.getElementById("error_log_list");

  console.log("trying to prepend error item:", error_log_item)

  error_log_list.prepend(error_log_item)
}

function get_error_log_item_from_error(error) {
  /* function to return an HTML element to be added into the error log
   *
   * Inputs:
   *    error: the error field of some response sent from the server
   *
   * Outputs:
   *    a list item element <li> containing whatever
   *    I want it to have to display the error
   */
  let output_list_element = document.createElement("li")
  let formatted_error_text = format_error_string_for_log(error)

  output_list_element.textContent = formatted_error_text

  output_list_element.className = "error_log_list_item"

  return output_list_element
}

function format_error_string_for_log(error) {
  /* function to take in an error from a response and format
   * it however I want to be displayed in the error log
   *
   * Inputs: 
   *    error: error field of a server response
   *
   *    of format:
   *    error = {
          "code": A numeric code for the error.
          "message": A string with a brief, concise error message.
          "data": An object containing additional data about the error. 
                    **A more detailed error description may be 
                    **included in a "details" member.
        }
   *
   *
   * Outputs:
   *    string: some string of to be used as the text for
   *            some error log entry
   */
  // let code = error.code
  let short_message = error.message

  // data is optional
  let data = error.data
  let details
  let output_string

  if (data) {
    if ("details" in data) {
      details = data.details
      output_string = details
    } else {
      output_string = short_message
    }
  } else {
    output_string = short_message
  }

  return output_string
}

function call_appropriate_callback(response) {
  /* function to take in a valid and successful response
   * and properly call on the callback function corresponding
   * to the message
   *
   * Inputs:
   *    response: a response that has a "result" field and 
   *              is valid based on validate_response(), meaning that 
   *              the request this response coresponds to was successful
   *
   * Outputs:
   *    none, 
   *
   * Side Affects:
   *   calls the appropriate callback for the message
   */
  console.log("trying to find appropriate callback for successful response", response)
  const response_id = response.id

  let queue_callback_function = sent_message_queue[response_id]
  // https://stackoverflow.com/questions/13417000/synchronous-request-with-websockets
  if (typeof (queue_callback_function) == 'function') {

    queue_callback_function(response);

  } else {
    console.warn("failed to find function associated with response_id")
  }

}

function validate_response(response) {
  /* takes in a fresh response from the server 
   * and validates that it has the correct fields and field structure.
   *
   *  Inputs:
   *    chimera response message  object that is was fed into `parse_response()`
   *
   *  Outputs: 
   *      list containing two elements:
   *        [boolean, string]
   *        boolean: True if the response is valid
   *                 False if there are any formatting problems
   *                  - no ID, 
   *                  - response ID not being the message queue
   *                  - no error or response
   *                  - both error and response
   *        string: (provided the response is valid),
   *                this string is the type of response,
   *                which will either be 
   *                - "error", for a response with an error field
   *                - "success", for a response with a result field
   *                - null, for an invalid response
   *
   *  Side Affects:
   *      if the response is invalid, but contains an ID 
   *      in the queue, then we will remove that entry from the queue
   *      
   *      this is because I am considering invalid responses as garbage
   *      that will not be processed any further.
   *
   *      but if the ID is in the queue, then it must be removed
   *      or else it will linger unresolved, potentially 
   *      causing memory problems
   *   */

  // default values for return values 
  let is_response_valid = false
  let response_type = null
  // the important part of a reponse is that it either 
  // has a "result" field containing the information about the successfully
  // fulfilled request, or an "error" field 
  const response_has_error = response.hasOwnProperty("error")
  const response_has_result = response.hasOwnProperty("result")
  const response_has_id = response.hasOwnProperty("id")

  // variable to keep track of whether the ID of
  // the response has an entry in the queue
  // if the response lacks an id field, this will still
  // evaluate to false
  let response_id_in_queue = response.id in sent_message_queue

  // check all different error cases
  // no id
  // id not in queue
  // error & result
  // !err & !res
  if (!response_has_id) {
    console.error("received response with no ID:", response)

  } else if (!response_has_error && !response_has_result) {
    console.error("recieved response that doesn't have an error nor result:", response)

  } else if (response_has_error && response_has_result) {
    console.error("recieved response that had error AND response:", response)

  } else if (!response_id_in_queue) {
    // if the code has gotten up to this `else if`, 
    // that means that the response has an 
    // "id" field and has either an error or a result
    // so if that id of a properly formatted message
    // is not in the queue, then we've received a response that 
    // doesn't correspond to any sent out messages
    // 
    // (potential TODO) add a sent_message_id history
    // so we can check if this response is to a previous message
    // or just sent erroenously
    console.error("recieved valid response with message_id not in the message queue", response, JSON.stringify(sent_message_queue, null, 2))

  } else {
    // if none of the above statements have gotten triggered
    // then we have a valid response
    is_response_valid = true

    if (response_has_error) {
      response_type = "error"
    } else if (response_has_result) {
      // checking this way to guarentee I'm
      // only assigning the type
      // when the response has it, instead
      // of doing `if error, else`
      response_type = "success"
    }
  }

  // final check to see if we need to delete an entry
  // in the queue for an invalid message
  if (response_id_in_queue && !is_response_valid) {
    console.log("removing message queue item for invalid response", response)
    delete sent_message_queue[response.id]
  }

  // finally, return whatever has been filled in
  return [is_response_valid, response_type]
}
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
  const random_string = (len, chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') => [...Array(len)].map(() => chars.charAt(Math.floor(Math.random() * chars.length))).join('');
  const salt = random_string(5);

  const id = hostname + "-" + port + '- ' + salt;
  return id;
}

function updateClipboard(newClip) {
  navigator.clipboard.writeText(newClip).then(
    () => {
      /* clipboard successfully set */
      console.log("shoulda copied [", newClip, "] to clipboard");
    },
    () => {
      /* clipboard write failed */
      console.log("couldn't write", newClip, "to clipboard");
    },
  );
}

function create_message_for_game_move(player_move_string) {
  /*
   * creates a game-action request message in Chimera
   * format from the move a player wants to perform
   *
   * type : request
   * operation : game_action
   * id : NOT FILLED IN HERE, as id assignment is controlled by `send_message`
   *      
   * params: {
   *    match-id : 
   *    action : "move"
   *    data : {
   *        "move": "rock"
   *    }
   * }
   *
   * Inputs:
   *    player_move_string: the string for whatever move the player is doine
   *                        should be rock,paper,scissors,lizard,or spock
   *                        however validation is handled by game logic
   *                        so we don't check validity of move here
   *
   */
  // general part of message
  let message = {};
  message.type = "request";
  message.operation = "game-action";

  // fill in params
  let params = {};
  params["match-id"] = MATCH_ID
  params.action = "move"

  // fill in params data
  let data = {}
  data.move = player_move_string

  params.data = data

  message.params = params

  return message

}

// BOOTSTRAP EVENT LISTENERS

function registerTable(table) {
  /* function to take in a table, and add any event listeners I want
   * at least will be on click to send messages
   */

  console.log("registering table")
  // Add an event listener to the table div that listens to when any of the buttons are clicked
  table.addEventListener("click", function(event) {
    // Check if the event target is a button element
    if (event.target.tagName == "BUTTON") {
      // Get the word associated with the button
      let word = event.target.innerText;
      // Assume that this function returns an object with some properties
      let game_action_message = create_message_for_game_move(word);

      console.log("formed message for game-action:", game_action_message);

      send_message(game_action_message, websocket, handle_game_action);
    }
  });

}
function initGame() {

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
        "match-id": join_match_id,
        "player-name": "player2"
      }
      message.params = params
      callback_function = handle_join_match


      // SPECTATING MATCH
    } else if (spectate_match_id) {
      // spectating match
      message.operation = "spectate-match"
      const params = {
        // TODO remove these once we've updated chimera to 
        // not need a game parameter for Join and Create match
        "game": "rockpaperscissors",
        "match-id": spectate_match_id,
        "player-name": "player2"
      }
      message.params = params

      // CREATING MATCH
    } else {
      // TODO make global utils to store the information
      // about message format so message.operation = ... 
      // could be a global variable call
      message.operation = "create-match"
      const params = {
        // game ID is just the lowercase Python Class name
        "game": "rockpaperscissors",
        "player-name": "player1"
      };

      message.params = params;

      callback_function = handle_create_match;
      //console.log("create match callback function defined");
      //console.log("typeof callback is:",typeof(callback_function));
      //console.log("callback is:",callback_function);
    }
    send_message(message, websocket, callback_function)
  });
}

function listen() {
  /** listen to any incoming message and parse it **/
  websocket.addEventListener("message", ({ data }) => {
    // receive message from the server
    const message = JSON.parse(data);
    switch (message.type) {
      case "request":
        showMessage("server sent request to user, this is fucked up <<<", message);
        break;

      case "notification":
        console.log("received notification <<<", message)
        break;

      case "response":
        console.log("received response <<<", message)
        parse_response(message, websocket)
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

  // GLOBAL VARIABLE ASSIGNMENT
  websocket = new WebSocket(websocket_address);


  // GLOBAL VARIABLE ASSIGNMENT
  client_id = generate_user_id()


  // listening for someone opening a websocket
  initGame()

  // listen for messages
  listen()
});
