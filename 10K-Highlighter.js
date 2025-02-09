// ==UserScript==
// @name         Highlighter
// @namespace    http://tampermonkey.net/
// @version      2025-02-08
// @description  Highlight key words
// @author       You
// @match        file:///*/10K/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=undefined.
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    function highlight(text) {
        var regex = new RegExp(text, "gi");

        // Iterate over all text nodes and replace matches
        function recursiveHighlight(element) {
            if (element.nodeType === Node.TEXT_NODE) {
                var matches = element.nodeValue.match(regex);
                if (matches) {
                    var span = document.createElement('span');
                    span.innerHTML = element.nodeValue.replace(regex, function(match) {
                        return "<span class='highlight'>" + match + "</span>";
                    });
                    element.parentNode.insertBefore(span, element);
                    element.remove();
                }
            } else if (element.nodeType === Node.ELEMENT_NODE && element.tagName !== 'SCRIPT' && element.tagName !== 'STYLE') {
                Array.from(element.childNodes).forEach(recursiveHighlight);
            }
        }

        recursiveHighlight(document.body);
    }


    // Words to highlight
    var words = [
        '\\b\\$[0-9,.]+(?:\\s+\\w+)*\\s*(?:million|billion)\\b',
        '\\b(?:billion|million)\\b',
        'notional amounts outstanding', 'notional amount',
        'hedging instrument', 'derivative instrument',
        'derivative not designated', 'derivatives not designated',
        'reclassified from aoci into income',
        'cash flow hedging', 'swap contract', 'forward contract',
        'fair value of derivative', 'excluded from effectiveness testing', 'net investment',
        'income on derivative', 'interest rate swap', 'financial instrument',
        'foreign exchange contract', 'foreign exchange','forward exchange contract', 'forward exchange',
        'foreign currency',

        '\\bgain\\b', '\\bloss\\b',
        '\\boci\\b', '\\baoci\\b', 'cash flow', 'notional', 'hedge', 'derivative', 'fair value'
    ];
    // Iterate over the words and highlight them
    for (var i = 0; i < words.length; i++) {
        highlight(words[i]);
    }

    // Add CSS for highlighting
    var style = document.createElement('style');
    style.innerHTML = ".highlight { background-color: yellow; font-weight: bold; }";
    document.head.appendChild(style);

    // Optionally, you can log a message when the script runs
    console.log("Highlighter script executed.");
})();
