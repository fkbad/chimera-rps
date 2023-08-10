
/* 
 * File to create the html for the table that Rock Paper Scissors
 * will be played upon*/


function createTable(table) {
  /*
   * function to actually create the HTML for the table
   *
   * Inputs:
   *    table: the table class div from the rps html file
   *    game_id: the game_id variant to play, taken from URLParams
   */

  console.log("creating table...")
  // first get the game_id from the URL
  const url_params = new URLSearchParams(window.location.search)

  // search params uses dict-like get syntax
  // has separate method to check whether or not a field is in the URL
  const game_id = url_params.get("game_id");

  if (!game_id) {
      table.innerText = "No subgame chosen";
    return
  };

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

  // after the fieldset has been populated, add it to the table
  table.appendChild(fieldset)
}

// Export the createTable function using a named export
export { createTable };


