// Custom Virtual Keyboard for Touch Screen
class VirtualKeyboard {
    constructor() {
        this.isVisible = false;
        this.currentInput = null;
        this.keyboard = null;
        this.init();
    }

    init() {
        this.createKeyboard();
        this.attachEventListeners();
    }

    createKeyboard() {
        // Create keyboard container
        const keyboardContainer = document.createElement('div');
        keyboardContainer.id = 'virtual-keyboard';
        keyboardContainer.className = 'virtual-keyboard';
        keyboardContainer.innerHTML = `
            <div class="keyboard-header">
                <span>Virtual Keyboard</span>
                <button type="button" class="keyboard-close" onclick="virtualKeyboard.hide()">×</button>
            </div>
            <div class="keyboard-body">
                <div class="keyboard-row">
                    <button class="key" data-key="1">1</button>
                    <button class="key" data-key="2">2</button>
                    <button class="key" data-key="3">3</button>
                    <button class="key" data-key="4">4</button>
                    <button class="key" data-key="5">5</button>
                    <button class="key" data-key="6">6</button>
                    <button class="key" data-key="7">7</button>
                    <button class="key" data-key="8">8</button>
                    <button class="key" data-key="9">9</button>
                    <button class="key" data-key="0">0</button>
                    <button class="key" data-key="backspace">⌫</button>
                </div>
                <div class="keyboard-row">
                    <button class="key" data-key="q">Q</button>
                    <button class="key" data-key="w">W</button>
                    <button class="key" data-key="e">E</button>
                    <button class="key" data-key="r">R</button>
                    <button class="key" data-key="t">T</button>
                    <button class="key" data-key="y">Y</button>
                    <button class="key" data-key="u">U</button>
                    <button class="key" data-key="i">I</button>
                    <button class="key" data-key="o">O</button>
                    <button class="key" data-key="p">P</button>
                </div>
                <div class="keyboard-row">
                    <button class="key" data-key="a">A</button>
                    <button class="key" data-key="s">S</button>
                    <button class="key" data-key="d">D</button>
                    <button class="key" data-key="f">F</button>
                    <button class="key" data-key="g">G</button>
                    <button class="key" data-key="h">H</button>
                    <button class="key" data-key="j">J</button>
                    <button class="key" data-key="k">K</button>
                    <button class="key" data-key="l">L</button>
                    <button class="key" data-key="enter">Enter</button>
                </div>
                <div class="keyboard-row">
                    <button class="key" data-key="z">Z</button>
                    <button class="key" data-key="x">X</button>
                    <button class="key" data-key="c">C</button>
                    <button class="key" data-key="v">V</button>
                    <button class="key" data-key="b">B</button>
                    <button class="key" data-key="n">N</button>
                    <button class="key" data-key="m">M</button>
                    <button class="key" data-key="space">Space</button>
                </div>
            </div>
        `;

        document.body.appendChild(keyboardContainer);
        this.keyboard = keyboardContainer;
    }

    attachEventListeners() {
        // Add click listeners to all keys
        this.keyboard.addEventListener('click', (e) => {
            if (e.target.classList.contains('key')) {
                this.handleKeyPress(e.target.dataset.key);
            }
        });

        // Add touch listeners for better touch response
        this.keyboard.addEventListener('touchstart', (e) => {
            if (e.target.classList.contains('key')) {
                e.target.classList.add('key-pressed');
            }
        });

        this.keyboard.addEventListener('touchend', (e) => {
            if (e.target.classList.contains('key')) {
                e.target.classList.remove('key-pressed');
            }
        });
    }

    handleKeyPress(key) {
        if (!this.currentInput) return;

        if (key === 'backspace') {
            this.currentInput.value = this.currentInput.value.slice(0, -1);
        } else if (key === 'space') {
            this.currentInput.value += ' ';
        } else if (key === 'enter') {
            this.hide();
            return;
        } else {
            this.currentInput.value += key;
        }

        // Trigger input event
        this.currentInput.dispatchEvent(new Event('input', { bubbles: true }));
    }

    show(inputElement) {
        this.currentInput = inputElement;
        this.keyboard.style.display = 'block';
        this.isVisible = true;
        
        // Scroll to keyboard
        setTimeout(() => {
            this.keyboard.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }, 100);
    }

    hide() {
        this.keyboard.style.display = 'none';
        this.isVisible = false;
        this.currentInput = null;
    }

    toggle(inputElement) {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show(inputElement);
        }
    }
}

// Initialize virtual keyboard
const virtualKeyboard = new VirtualKeyboard();

// Make it globally available
window.virtualKeyboard = virtualKeyboard;
