// increasing counter for sent out message ID's
// this + the created client ID should form a unique id per message
// across users
let next_message_id = 0

// Function to get the form values
function getFormValues(form) {
  // Create a new FormData object from the form element
  var formData = new FormData(form);
  // Get the selected value of the dropdown
  var value = formData.get("dropdown");
  console.log("form value:" , value);
  // Return the value
  return value;
}

// Function to validate the dropdown selection
function validateGameChoiceForm(form_value) {
  // make sure that the form is not empty
  // and that the player actually chose a game
  if (form_value == "") {
    alert("Please select an option from the dropdown");
    return false;
  }
  // Otherwise, return true
  return true;
}

function listen_for_form(websocket) {
  // Get the form element by its id or any other selector
  var form = document.querySelector("#game-submission-form");
  console.log("found item", form)
  // Add an event listener to the submit event of the form element
  form.addEventListener("submit", function(event) {
    // Prevent the default behavior of the submit event
    event.preventDefault();
    // Call the function and get the selected value
    var value = getFormValues(form);
    const is_value_valid = validateGameChoiceForm(value)

    if (!is_value_valid) {
      // invalid value provided
      return
    }

    // Get the current URI
    var uri = window.location.href;
    // Append the selected value as a parameter named "game_id"
    var newUri = uri + "games/play.html?game_id=" + value;
    // Redirect the user to the new URI
    console.log("sending user to new URI:",newUri)
    window.location.assign(newUri);
  });
}
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

  // listening for someone opening a websocket
  initGame(websocket)

  // listen for messages
  listen(websocket)

  listen_for_form(websocket)
});

function initGame(websocket) {
  //function to start a game upon the initialization of a websocket
  websocket.addEventListener("open", () => {

    // this returns a dictionary
    const url_params = new URLSearchParams(window.location.search)

    console.log("connection opened :)")

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
