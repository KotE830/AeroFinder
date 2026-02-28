// content.js - Injected into the page to handle element selection
let isActive = false;
let currentHighlighted = null;
let overlayPanel = null;
// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "ACTIVATE_SELECTOR") {
        isActive = true;
        enableSelectionMode();
    }
    else if (request.action === "DEACTIVATE_SELECTOR") {
        isActive = false;
        disableSelectionMode();
    }
});
function enableSelectionMode() {
    document.addEventListener("mouseover", handleMouseOver, true);
    document.addEventListener("mouseout", handleMouseOut, true);
    document.addEventListener("click", handleClick, true);
    createOverlay();
}
function disableSelectionMode() {
    document.removeEventListener("mouseover", handleMouseOver, true);
    document.removeEventListener("mouseout", handleMouseOut, true);
    document.removeEventListener("click", handleClick, true);
    if (currentHighlighted) {
        currentHighlighted.classList.remove("aerofinder-highlight-hover");
        currentHighlighted = null;
    }
    removeOverlay();
}
function handleMouseOver(event) {
    if (!isActive)
        return;
    // Ignore our own overlay
    if (event.target.closest('#aerofinder-overlay-panel'))
        return;
    if (currentHighlighted) {
        currentHighlighted.classList.remove("aerofinder-highlight-hover");
    }
    currentHighlighted = event.target;
    currentHighlighted.classList.add("aerofinder-highlight-hover");
}
function handleMouseOut(event) {
    if (!isActive)
        return;
    if (currentHighlighted) {
        currentHighlighted.classList.remove("aerofinder-highlight-hover");
        currentHighlighted = null;
    }
}
function handleClick(event) {
    if (!isActive)
        return;
    // Ignore clicks inside our overlay
    if (event.target.closest('#aerofinder-overlay-panel'))
        return;
    event.preventDefault();
    event.stopPropagation();
    const target = event.target;
    const selector = generateCssSelector(target);
    const textContent = target.innerText || target.textContent || "";
    updateOverlay(selector, textContent.trim().substring(0, 50));
}
function generateCssSelector(el) {
    if (el.tagName.toLowerCase() === "html")
        return "html";
    if (el.tagName.toLowerCase() === "body")
        return "body";
    let path = [];
    let current = el;
    // Go up 3 levels maximum to keep the selector relatively simple but specific enough
    let depth = 0;
    while (current && current.tagName.toLowerCase() !== "html" && depth < 4) {
        let selector = current.tagName.toLowerCase();
        // Classes
        const classes = Array.from(current.classList).filter(c => c !== 'aerofinder-highlight-hover');
        if (classes.length > 0) {
            // Use up to first 2 classes to avoid overly long selectors, and avoid randomly generated strings if possible
            const validClasses = classes.filter(c => !/\d/.test(c)).slice(0, 2);
            if (validClasses.length > 0) {
                selector += '.' + validClasses.join('.');
            }
            else {
                selector += '.' + classes[0]; // fallback
            }
        }
        path.unshift(selector);
        current = current.parentElement;
        depth++;
    }
    return path.join(" > ");
}
function createOverlay() {
    if (document.getElementById('aerofinder-overlay-panel'))
        return;
    const panel = document.createElement('div');
    panel.id = 'aerofinder-overlay-panel';
    panel.innerHTML = `
    <h3>AeroFinder Scraper</h3>
    <div style="font-size:12px; color:#555;">클릭해서 요소를 선택하세요.</div>
    <div class="content-preview" id="af-preview">내용 미리보기: 선택 안됨</div>
    <div class="selector-result" id="af-result">태그를 클릭하면 여기에 경로가 나타납니다.</div>
    <div class="button-group">
      <button id="af-btn-copy">경로 복사</button>
      <button id="af-btn-close" class="btn-close">종료</button>
    </div>
  `;
    document.body.appendChild(panel);
    document.getElementById('af-btn-copy').addEventListener('click', () => {
        const text = document.getElementById('af-result').innerText;
        if (text && text.length > 0) {
            navigator.clipboard.writeText(text).then(() => {
                showToast("클립보드에 복사되었습니다!");
            });
        }
    });
    document.getElementById('af-btn-close').addEventListener('click', () => {
        isActive = false;
        disableSelectionMode();
    });
}
function showToast(message) {
    // Remove existing toast if any
    const existing = document.getElementById('aerofinder-toast-msg');
    if (existing)
        existing.remove();
    const toast = document.createElement('div');
    toast.id = 'aerofinder-toast-msg';
    toast.className = 'aerofinder-toast';
    toast.innerText = message;
    document.body.appendChild(toast);
    // Trigger animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    // Hide and remove after 2 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 300);
    }, 2000);
}
function updateOverlay(selector, preview) {
    const resultDiv = document.getElementById('af-result');
    const previewDiv = document.getElementById('af-preview');
    if (resultDiv && previewDiv) {
        resultDiv.innerText = selector;
        previewDiv.innerText = `미리보기: ${preview || '(텍스트 없음)'}`;
    }
}
function removeOverlay() {
    const panel = document.getElementById('aerofinder-overlay-panel');
    if (panel) {
        panel.remove();
    }
}
