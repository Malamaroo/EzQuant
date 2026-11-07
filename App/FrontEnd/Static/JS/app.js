const button = document.getElementById('HelloButton');
const output = document.getElementById('HelloMessage');

button.addEventListener('click', async () => {
    const response = await fetch('/api/hello');   // visit the Flask URL, like you did in Step 1
    const data = await response.json();           // turn the reply into a JS object (like a dict)
    output.textContent = data.message + ' The number is ' + data.number;
});

async function loadStockList() {
    const response = await fetch('/api/stocks');
    const data = await response.json();
    const stockListDiv = document.getElementById('stock_list');

    for (const stock of data.stocks) {
        const row = document.createElement('div');
        row.className = 'stock-row';
        row.innerHTML = `
            <label><input type="checkbox" class="stock-checkbox" value="${stock}"> ${stock}</label>
            $<input type="number" class="stock_amount" id="amount-${stock}" min="5000" step="1000" placeholder="Amount">
        `;
        stockListDiv.appendChild(row);
    }
}

loadStockList();

const saveButton = document.getElementById('save_portfolio_button');
const saveMessage = document.getElementById('save_portfolio_message');

saveButton.addEventListener('click', async () => {
    // 1. Build a list of the stocks the user ticked
    const holdings = [];
    const checkboxes = document.querySelectorAll('.stock-checkbox');

    for (const checkbox of checkboxes) {
        if (checkbox.checked) {
            const stock = checkbox.value;
            const amount = Number(document.getElementById(`amount-${stock}`).value);
            holdings.push({ stock: stock, value: amount });
        }
    }

    // 2. Send it to Python
    const response = await fetch('/api/portfolio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ portfolio: holdings }),
    });
    const data = await response.json();

    // 3. Show Python's reply
    if (!response.ok) {
        portfolioMessage.textContent = data.error;
        return;
    }
    saveMessage.textContent = `${data.message} Cash left: $${data.cash_left.toLocaleString()}`;
});

// ===== Step 2: Find a hedge =====
const hedgeButton = document.getElementById('hedge_portfolio_button');
const hedgeMessage = document.getElementById('hedge_portfolio_message');

hedgeButton.addEventListener('click', async () => {
    hedgeMessage.textContent = 'Calculating...';

    const response = await fetch('/api/hedge');
    const data = await response.json();

    hedgeMessage.textContent = `The best stock to hedge your portfolio is ${data.stock_recommendation} (covariance: ${data.covariance_value.toFixed(6)})`;
});

// ===== Reset portfolio =====
const resetButton = document.getElementById('reset_portfolio_button');

resetButton.addEventListener('click', async () => {
    // 0. Double-check, since this deletes their portfolio
    if (!confirm('Are you sure you want to reset your portfolio?')) {
        return;
    }

    // 1. Clear the page
    for (const checkbox of document.querySelectorAll('.stock-checkbox')) {
        checkbox.checked = false;
    }
    for (const amountBox of document.querySelectorAll('.stock-amount')) {
        amountBox.value = '';
    }
    hedgeMessage.textContent = '';

    // 2. Clear the saved file
    const response = await fetch('/api/portfolio/reset', { method: 'POST' });
    const data = await response.json();
    saveMessage.textContent = data.message;
});
