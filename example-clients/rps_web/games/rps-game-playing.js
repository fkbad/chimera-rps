
// adding this variable to keep track of the most 
// recently sent message, so when the client
// recieves a response it knows what request it is 
// associated with. Allows for more confident parsing 
// of incoming messages
//
// Eg: When I know that I just sent a spectate-match operation
// then I recieve and error, I can provide more context
// to the error
//
// Not sure if this would need to be a queue of some kind
// to handle server delay. Under the situation that 
// the client sends two messages before the server can 
// handle the first request
//
// Leaving as single variable for now for simplicity
let last_sent_unresolved_message = null;


// increasing counter for sent out message ID's
// this + the created client ID should form a unique id per message
// across users
let next_message_id = 0


function send_message(message,websocket) {
  /** takes a fully formatted, non-jsoned message
   * and sends it to the websocket 
   *
   * standardized through helper function to I can unify debugging statements*/

  // triple equals checks if something is *exactly* null
  // let var = null is the only thing that should trip this
  //
  // !== checks if somethin is ANYTHING but = null
  // this includes being unassigned
  //
  // so like if I had variable instantiated like: 
  //  let new_variable;
  // then new_variable !== null is True
  // whereas, if we did != null, then it would be False

  // if (last_sent_unresolved_message !== null) {
  //   // there is still some unresolved message
  //   showMessage("tried sending message while there was an unresolved message :",last_sent_unresolved_message);
  //   return
  // } 

  // no unresolved message
  last_sent_unresolved_message = message

  const stringified_message_id = String(next_message_id)
  const message_id_to_append = "-" + stringified_message_id
  message["id"] += message_id_to_append
  next_message_id += 1

  console.log("sending >>> ",message)
  websocket.send(JSON.stringify(message));
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

function getWebSocketServer() {
  if (window.location.host === "fkbad.github.io") {
    return "wss://sylv-connect4-ba23863cf42a.herokuapp.com/";
  } else if (window.location.host === "localhost:8000") {
    return "ws://127.0.0.1:14200";
  } else {
    throw new Error(`Unsupported host: ${window.location.host}`);
  }
}

// overall initializer, the bootstrap or "main"
window.addEventListener("DOMContentLoaded", () => {
  // Open the WebSocket connection and register event handlers.
  // port specified in main() of `app.py`

  const websocket_address = getWebSocketServer()
  const websocket = new WebSocket(websocket_address);

  const user_id = generate_user_id()
  //
  // listening for someone opening a websocket
  initGame(user_id,websocket)

  // listen for messages
  listen(user_id,websocket)

  const list_games_button = document.querySelector(".button")
  send_list_message_on_click(user_id,list_games_button,websocket)
  

});

function initGame(id,websocket) {

  //function to start a game upon the initialization of a websocket
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
      "id": id
    }

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
      }
      message.params = params
    }
    send_message(message,websocket)
  });
}



function listen(id,websocket) {
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
        // parse_response(id,message,websocket)
        break;

      default:
        throw new Error(`Unsupported event type: ${message.type}.`);
    }
  });
}


// function parse_response(id,response,websocket) {
//   /** function to take in any kind of response and handle it */
//   
// }

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

