// background.js - Listens for extension icon clicks to toggle the selector tool
let isSelectorActive = false;
chrome.action.onClicked.addListener((tab) => {
    // We toggle the state and send a message to the content script in the active tab
    isSelectorActive = !isSelectorActive;
    if (isSelectorActive) {
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ['content.js']
        }).then(() => {
            chrome.tabs.sendMessage(tab.id, { action: "ACTIVATE_SELECTOR" });
        }).catch(err => console.error("Script injection failed:", err));
    }
    else {
        chrome.tabs.sendMessage(tab.id, { action: "DEACTIVATE_SELECTOR" });
    }
});
