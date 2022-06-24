'use strict';

const NUM_BINS = 10;

const STATE_NAMES = {
  0: 'Load',
  1: 'Execute',
  2: 'Recycle',
  3: 'Stopped',
  4: 'Error'
};

var nStep;
var state;
var bins = [[], [], [], [], [], [], [], [], [], []];
var curInstruction;
var curParam;

// Runs only once, sets up the HTML.
function setup() {
  for (let i = 0; i < NUM_BINS; ++i) {
    let headerDiv = $('<div>');
    headerDiv.addClass('bin-header')
    headerDiv.css('grid-area', '1 / ' + (i+1) + ' / auto / auto');
    headerDiv.text('Bin ' + i)
    let binDiv = $('<div id="bin' + i + '">')
    binDiv.addClass('bin');
    binDiv.css('grid-area', '2 / ' + (i+1) + ' / auto / auto');
    $('#bins').append(headerDiv).append(binDiv);
  }
}

// Resets all internal variables to their initial state.
function resetState() {
  bins[0] = new Array(20).fill(0);
  for (let i = 1; i < NUM_BINS; ++i) {
    bins[i] = [];
  }
  nStep = 0;
  state = 0;
  curInstruction = undefined;
  curParam = undefined;

  $('#termination-msg').text('');
}

function makeShirtElem(color) {
  let shirt = $('<div>').addClass('shirt').addClass('shirt' + color);
  shirt.text(color);
  return shirt;
}

// Copies `bins` variable to the HTML, ensuring that any previous HTML was
// cleared.
function populateHtmlBins() {
  for (let i = 0; i < NUM_BINS; ++i) {
    let bin = $('#bin' + i);
    bin.empty();
    for (let j = 0; j < bins[i].length; ++j) {
      bin.append(makeShirtElem(bins[i][j]));
    }
  }
}

function populateHtmlStatement() {
  $('#curr-step-num').text(nStep);
  $('#curr-state').text(STATE_NAMES[state]);
  $('#curr-instruction-wrapper').empty();
  if (typeof curInstruction !== 'undefined') {
    $('#curr-instruction-wrapper').append(makeShirtElem(curInstruction));
  }
  $('#curr-param-wrapper').empty();
  if (typeof curParam !== 'undefined') {
    $('#curr-param-wrapper').append(makeShirtElem(curParam));
  }
}

function populateHtml() {
  populateHtmlBins();
  populateHtmlStatement();
}

$(document).ready(() => {
  setup();
  resetState();
  populateHtml();
});

function reportMsg(msg) {
  $('#termination-msg').text(msg);
}

function loadInstructionsFromInput() {
  const input = $('#input-textbox').val();
  for (let i = 0; i < input.length; ++i) {
    let color = parseInt(input[i])
    if (isNaN(color)) {
      reportMsg('Invalid input character: "' + input[i] + '"');
    }
    bins[1].push(color);
  }
}

function onReload() {
  resetState();
  loadInstructionsFromInput();
  populateHtml();
}

function popBin(bin) {
  // Note: This function also updates the HTML.
  if (bins[bin].length === 0) {
    throw 'Attempting to get shirt from empty bin ' + bin;
  }
  $('#bin' + bin).find('.shirt:first').remove();
  return bins[bin].shift();
}

function pushBin(bin, color) {
  // Note: This function also updates the HTML.
  $('#bin' + bin).prepend(makeShirtElem(color));
  bins[bin].unshift(color);
}

function onStep() {
  try {
    switch (state) {
      case 0:  // Load
        curInstruction = popBin(1);
        curParam = popBin(1);
        state = 1;  // Execute
        populateHtmlStatement();
        break;

      case 1: // Execute
        executeCurStatement();
        if (state != 3) {
          state = 2;  // Recycle
        }
        populateHtmlStatement();
        break;

      case 2:  // Recycle
        pushBin(2, curInstruction);
        pushBin(2, curParam);
        curInstruction = undefined;
        curParam = undefined;
        state = 0;
        ++nStep;
        populateHtmlStatement();
        break;

      case 3:  // Stopped
      case 4:  // Error
        populateHtmlStatement();
        break;
    }
  } catch (err) {
    reportMsg('Aborted: ' + err);
    state = 4;
    populateHtmlStatement();
  }
}

function executeCurStatement() {
  switch (curInstruction) {
    case 0:  // STOP
      reportMsg('Execution complete.');
      state = 3;
      return;

    case 1:  // LOAD
      pushBin(3, popBin(curParam));
      return;

    case 2:  // STORE
      pushBin(curParam, popBin(3));
      return;

    case 3:  // ADD
      pushBin(3, (popBin(3) + curParam) % 10);
      return;

    case 4:  // MUL
      pushBin(3, (popBin(3) * curParam) % 10);
      return;

    case 5:  // NOP
    case 6:  // NOP
    case 7:  // NOP
      return;

    case 8:
      bins[bins[3][0]].reverse();
      populateHtmlBins();
      return;

    case 9:
      let targetBin = bins[3][0];
      let temp = bins[curParam];
      bins[curParam] = bins[targetBin];
      bins[targetBin] = temp;
      populateHtmlBins();
      return;
  }
}
