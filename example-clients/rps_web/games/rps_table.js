
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

    // Declare an array of words for the buttons using let
    const moves = ["rock","paper","scissors","lizard","spock"]

    // Check the game_id and create the buttons accordingly
    if (game_id == "rps") {
        // Create three buttons using let
        for (let i = 0; i < 3; i++) {
            // Create a button element using const
            const button = document.createElement("button");
            // Set the button text to the word at index i
            button.innerText = moves[i];
      //
            // Append the button to the table div
            table.appendChild(button);
        }
    } else if (game_id == "rpsls") {
        // Create five buttons using let
        for (let i = 0; i < 5; i++) {
            // Create a button element using const
            const button = document.createElement("button");
            // Set the button text to the word at index i
            button.innerText = moves[i];
            // Append the button to the table div
            table.appendChild(button);
        }
    } else {
        // Display an error message
        table.innerText = "Invalid game chosen";
    }
}

// Export the createTable function using a named export
export { createTable };
