
/* 
 * File to create the html for the table that Rock Paper Scissors
 * will be played upon*/


function createTable(table) {
  /* create the table FR
   */
  const move_fieldset = return_move_fieldset(table)

  const table_display = return_table_display()

  table.appendChild(table_display)
  table.appendChild(move_fieldset)
}

function return_table_display() {
  /* create the square board for the table
   */
  let display = document.createElement("div")
  display.id = "table_display"

  let fieldset = document.createElement("fieldset")
  fieldset.id = "table_display_fieldset"

  let legend = document.createElement("legend");
  legend.id = "table_display_legend"
  legend.innerText = "Current Round"

  // div to store the boxes and text
  let boxes = document.createElement("div");
  boxes.id = "table_display_boxes"

  populate_display_boxes(boxes)

  fieldset.appendChild(legend)
  fieldset.appendChild(boxes)

  display.appendChild(fieldset)

  return display
}

function populate_display_boxes(boxes) {
  /* function to populate the boxes div of the display
   * with the boxes and text representing the current round
   *
   * Inputs:
   *    boxes: div inside the table display fieldset
   *           with ID "table_display_boxes"
   *
   * Outputs;
   *    nothing
   *
   * Side Affects:
   *    creates 2 boxes to hold moves
   *    and adds them to the provided boxes div
   */
  let your_box = create_one_captioned_move_box("Your Move","player")
  boxes.appendChild(your_box)

  let opponent_box = create_one_captioned_move_box("Opponent's Move","opponent")


  boxes.appendChild(opponent_box)
}

function create_one_captioned_move_box(caption_text,id) {
  /* creates a move_box with caption
   * This includes both a caption describing what the 
   * box contains, as well as the box itself
   * 
   * Inputs:
   *    caption_text: string for the text to put on top
   *    of the move displaying box
   *
   *    id: the front part of the ID for the move_box
   *        used for identification of the move_box for updating the players move
   *
   * Outputs:
   *    a <div> element of class "captioned_move_box"
   *    containing the move_box and caption
   */
  // this will be the finally returned div we shove
  // the elements into
  let captioned_move_box = document.createElement("div");
  captioned_move_box.className = "captioned_move_box"

  let caption = document.createElement("a");
  caption.textContent = caption_text
  // could also add ID based on player/opponent
  caption.className = "move_box_caption"

  let move_box = document.createElement("div")
  // class with CSS styling from the react tutorial
  // https://react.dev/learn/tutorial-tic-tac-toe
  move_box.className = "move_box"

  if (id === "player") {
    move_box.id = "player_move_box"
  } else if (id === "opponent") {
    move_box.id = "opponent_move_box"
  } else {
    move_box.id = "other_move_box"
  }

  // order doesn't matter here as the classes
  // have a specified flex ordering 
  captioned_move_box.appendChild(caption)
  captioned_move_box.appendChild(move_box)

  return captioned_move_box
}



function return_move_fieldset(table) {
  /*
   * function to actually create the HTML for the table
   *
   * Inputs:
   *    table: the table class div from the rps html file
   *    game_id: the game_id variant to play, taken from URLParams
   */

  console.log("creating table...")
  
  let game_id = "rps"

  // Clear the table div
  table.innerHTML = "";

  let fieldset = document.createElement("fieldset");
  let legend = document.createElement("legend");
  let buttons = document.createElement("div");

  let title = document.getElementById("game_title")
  legend.innerText = "Pick Your Move :)"

  legend.id = "table_legend"
  buttons.id = "table_buttons"
  fieldset.id = "table_fieldset"

  fieldset.appendChild(legend)

  // Declare an array of words for the buttons using let
  const moves = ["rock","paper","scissors","lizard","spock"]

  // Check the game_id and create the buttons accordingly
  if (game_id == "rps") {
    // update the title
    title.innerHTML = "🪨 📜 ✂️ "

    for (let i = 0; i < 3; i++) {
        const button = document.createElement("button");
        // Set the button text to a move
        button.innerText = moves[i];
        // assign all the buttons to be part of the same class
        button.className = "table_button"
        // Append the button to the table div
        buttons.appendChild(button);
    }
  } else if (game_id == "rpsls") {
    title.innerHTML = "🪨 📜 ✂️ 🦎 🖖"
    // Create five buttons using let
    for (let i = 0; i < 5; i++) {
      // Create a button element using const
      const button = document.createElement("button");
      // Set the button text to the word at index i
      button.innerText = moves[i];
      // assign all the buttons to be part of the same class
      button.className = "table_button"
      // Append the button to the table div
      buttons.appendChild(button);
    }
  } else {
    title.innerHTML = "Invalid Game Chosen "
    // Display an error message
    table.innerText = "Invalid game chosen";
  }
  
  // after the buttons have been created, add them to the fieldset
  fieldset.appendChild(buttons)

  return fieldset
}

// Export the createTable function using a named export
export { createTable };


