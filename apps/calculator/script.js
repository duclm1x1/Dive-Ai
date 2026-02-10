/**
 * 🧮 iPhone Calculator Logic
 * Created by Dive AI V29.4
 * 
 * Features:
 * - Basic operations: +, -, ×, ÷
 * - Percentage
 * - Toggle sign (±)
 * - Decimal support
 * - Chain calculations
 */

// State
let currentOperand = '0';
let previousOperand = '';
let operation = null;
let shouldResetScreen = false;

// DOM Elements
const currentOperandElement = document.getElementById('current-operand');
const previousOperandElement = document.getElementById('previous-operand');

/**
 * Update display with current values
 */
function updateDisplay() {
    // Format number with commas
    let displayValue = currentOperand;

    if (currentOperand.length > 9) {
        // Use scientific notation for very long numbers
        displayValue = parseFloat(currentOperand).toExponential(5);
    } else {
        // Add thousand separators
        const parts = currentOperand.split('.');
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        displayValue = parts.join('.');
    }

    currentOperandElement.textContent = displayValue;

    // Show previous operand with operation
    if (previousOperand && operation) {
        previousOperandElement.textContent = `${previousOperand} ${operation}`;
    } else {
        previousOperandElement.textContent = '';
    }
}

/**
 * Append a number to current operand
 */
function appendNumber(number) {
    // Reset if needed (after calculation)
    if (shouldResetScreen) {
        currentOperand = '';
        shouldResetScreen = false;
    }

    // Limit length
    if (currentOperand.length >= 15) return;

    // Handle leading zero
    if (currentOperand === '0' && number !== '.') {
        currentOperand = number;
    } else {
        currentOperand += number;
    }

    updateDisplay();
}

/**
 * Append decimal point
 */
function appendDecimal() {
    if (shouldResetScreen) {
        currentOperand = '0';
        shouldResetScreen = false;
    }

    // Only one decimal allowed
    if (currentOperand.includes('.')) return;

    currentOperand += '.';
    updateDisplay();
}

/**
 * Clear all - AC button
 */
function clearAll() {
    currentOperand = '0';
    previousOperand = '';
    operation = null;
    shouldResetScreen = false;
    updateDisplay();
}

/**
 * Toggle positive/negative - ± button
 */
function toggleSign() {
    if (currentOperand === '0') return;

    if (currentOperand.startsWith('-')) {
        currentOperand = currentOperand.slice(1);
    } else {
        currentOperand = '-' + currentOperand;
    }

    updateDisplay();
}

/**
 * Calculate percentage - % button
 */
function percentage() {
    const current = parseFloat(currentOperand);

    if (previousOperand && operation) {
        // Percentage of previous operand
        const previous = parseFloat(previousOperand);
        currentOperand = String(previous * (current / 100));
    } else {
        // Just divide by 100
        currentOperand = String(current / 100);
    }

    updateDisplay();
}

/**
 * Set operation (+, -, ×, ÷)
 */
function setOperation(op) {
    // If there's a pending operation, calculate first
    if (operation !== null && !shouldResetScreen) {
        calculate();
    }

    operation = op;
    previousOperand = currentOperand;
    shouldResetScreen = true;

    updateDisplay();
}

/**
 * Calculate result - = button
 */
function calculate() {
    if (operation === null || previousOperand === '') return;

    const prev = parseFloat(previousOperand);
    const current = parseFloat(currentOperand);
    let result;

    switch (operation) {
        case '+':
            result = prev + current;
            break;
        case '-':
        case '−':
            result = prev - current;
            break;
        case '×':
            result = prev * current;
            break;
        case '÷':
            if (current === 0) {
                currentOperand = 'Error';
                previousOperand = '';
                operation = null;
                updateDisplay();
                setTimeout(clearAll, 1500);
                return;
            }
            result = prev / current;
            break;
        default:
            return;
    }

    // Format result
    currentOperand = formatResult(result);
    previousOperand = '';
    operation = null;
    shouldResetScreen = true;

    updateDisplay();
}

/**
 * Format calculation result
 */
function formatResult(result) {
    // Handle very small or very large numbers
    if (Math.abs(result) > 999999999 || (Math.abs(result) < 0.000001 && result !== 0)) {
        return result.toExponential(5);
    }

    // Round to avoid floating point issues
    const rounded = Math.round(result * 1000000000) / 1000000000;

    // Convert to string and limit decimal places
    let str = String(rounded);
    if (str.includes('.') && str.split('.')[1].length > 8) {
        str = rounded.toFixed(8);
        // Remove trailing zeros
        str = str.replace(/\.?0+$/, '');
    }

    return str;
}

/**
 * Keyboard support
 */
document.addEventListener('keydown', (event) => {
    const key = event.key;

    // Numbers
    if (/^[0-9]$/.test(key)) {
        appendNumber(key);
        return;
    }

    // Decimal
    if (key === '.' || key === ',') {
        appendDecimal();
        return;
    }

    // Operations
    switch (key) {
        case '+':
            setOperation('+');
            break;
        case '-':
            setOperation('-');
            break;
        case '*':
            setOperation('×');
            break;
        case '/':
            event.preventDefault();
            setOperation('÷');
            break;
        case 'Enter':
        case '=':
            calculate();
            break;
        case 'Escape':
        case 'c':
        case 'C':
            clearAll();
            break;
        case 'Backspace':
            if (currentOperand.length > 1) {
                currentOperand = currentOperand.slice(0, -1);
            } else {
                currentOperand = '0';
            }
            updateDisplay();
            break;
        case '%':
            percentage();
            break;
    }
});

// Initialize
updateDisplay();

console.log('🧮 iPhone Calculator loaded!');
console.log('🦞 Created by Dive AI V29.4');
