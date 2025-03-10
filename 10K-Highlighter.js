// ==UserScript==
// @name         Highlighter
// @namespace    http://tampermonkey.net/
// @version      2025-02-08
// @description  Highlight key words
// @author       You
// @match        file:///*/10K/*
// @match        https://www.sec.gov/Archives/edgar/data/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=undefined.
// @grant        none
// ==/UserScript==

(function () {
  "use strict";

  // Object to store word counts
  const wordCounts = {};

  function highlight(text) {
    var regex = new RegExp(text, "gi");
    let totalMatches = 0;

    // Iterate over all text nodes and replace matches
    function recursiveHighlight(element) {
      if (element.nodeType === Node.TEXT_NODE) {
        var matches = element.nodeValue.match(regex);
        if (matches) {
          totalMatches += matches.length;
        }
      } else if (
        element.nodeType === Node.ELEMENT_NODE &&
        element.tagName !== "SCRIPT" &&
        element.tagName !== "STYLE"
      ) {
        Array.from(element.childNodes).forEach(recursiveHighlight);
      }
    }

    recursiveHighlight(document.body);
    return totalMatches;
  }

  // Words to highlight
  var words = [
    "notional",
    "foreign currency",
    "interest rate swap",
    "cross currency",
    "cross-currency",
    "foreign exchange",
    "derivative liab",
    "futures contract",
    "options contract",
    "forward contract",
    "hedge",
    "hedging",
    "underlying asset",
    "counterparty",
    "collateral",
    "derivative liabilit",
    "warrant",
  ];
  setTimeout(() => {
    // Iterate over the words, highlight them, and store counts
    for (var i = 0; i < words.length; i++) {
      wordCounts[words[i]] = highlight(words[i]);
    }

    // Add CSS for highlighting
    var style = document.createElement("style");
    style.innerHTML =
      ".highlight { background-color: yellow; font-weight: bold; }";
    document.head.appendChild(style);

    // Log the results
    console.log("Highlighter script executed.");
    console.log("Word occurrence counts:");
    for (const [word, count] of Object.entries(wordCounts)) {
      if (count > 0)
        console.log(`"${word}": ${count} time${count === 1 ? "" : "s"}`);
    }
  }, 5000);
})();
