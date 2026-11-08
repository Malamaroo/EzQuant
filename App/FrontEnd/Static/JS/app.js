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


// ===== Step 3: Optimise =====
const riskInput = document.getElementById('risk_range_input');
const optimiseButton = document.getElementById('optimise_portfolio_button');
const optimiseMessage = document.getElementById('optimise_portfolio_message');
const optimisedPortfolioDiv = document.getElementById('optimised_portfolio');

optimiseButton.addEventListener('click', async () => {
    const risk = Number(riskInput.value);
    if (risk <= 0) {
        optimiseMessage.textContent = 'Please enter a target risk, e.g. 0.15 for 15% yearly volatility.';
        return;
    }

    optimiseMessage.textContent = 'Optimising...';
    optimisedPortfolioDiv.innerHTML = '';

    const response = await fetch('/api/optimise', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ yearly_risk: risk }),
    });
    const data = await response.json();

    if (!response.ok) {
        optimiseMessage.textContent = data.error;
        return;
    }

    optimiseMessage.textContent = 'Portfolio optimised and saved!';

    // Build a table, one row per stock
    let tableHtml = '<table><tr><th>Stock</th><th>Weight</th><th>Value</th></tr>';
    for (const row of data.new_portfolio) {
        tableHtml += `<tr>
            <td>${row.Stock}</td>
            <td>${(row.Weight * 100).toFixed(2)}%</td>
            <td>$${Math.round(row.Value).toLocaleString()}</td>
        </tr>`;
    }
    tableHtml += '</table>';
    optimisedPortfolioDiv.innerHTML = tableHtml;
});


// ===== Step 4: Backtest =====
const backtestStartInput = document.getElementById('backtest_start_date');
const backtestEndInput = document.getElementById('backtest_end_date');
const backtestButton = document.getElementById('backtest_button');
const backtestMessage = document.getElementById('backtest_message');
const backtestResults = document.getElementById('backtest_results');
const backtestChartCanvas = document.getElementById('backtest_chart');
const backtestDateRangeMessage = document.getElementById('backtest_date_range_message');
let backtestChart = null;      // holds the chart once it's drawn

async function loadBacktestDateRange() {
    const response = await fetch('/api/backtest/date-range');
    const data = await response.json();

    // Limit both date pickers to the dates we actually have
    backtestStartInput.min = data.first_date;
    backtestStartInput.max = data.last_date;
    backtestEndInput.min = data.first_date;
    backtestEndInput.max = data.last_date;

    // Pre-fill with the full range, so the user can just click Run
    backtestStartInput.value = data.first_date;
    backtestEndInput.value = data.last_date;

    backtestDateRangeMessage.textContent = `Data is available from ${data.first_date} to ${data.last_date}.`;
}

loadBacktestDateRange();

backtestButton.addEventListener('click', async () => {
    backtestMessage.textContent = 'Running backtest...';
    backtestResults.innerHTML = '';

    const response = await fetch('/api/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            start_date: backtestStartInput.value,
            end_date: backtestEndInput.value,
        }),
    });
    const data = await response.json();

    if (!response.ok) {
        backtestMessage.textContent = data.error;
        return;
    }
    backtestMessage.textContent = '';

    backtestResults.innerHTML = `
        <p>Final portfolio value: <strong>$${Math.round(data.final_portfolio_value).toLocaleString()}</strong></p>
        <p>Total return: <strong>${(data.total_return * 100).toFixed(2)}%</strong></p>
        <p>Backtest period: <strong>${data.years.toFixed(2)} years</strong></p>
        <p>Average annual return: <strong>${(data.average_annual_return * 100).toFixed(2)}%</strong></p>
        <p>P/E strategy final value: <strong>$${Math.round(data.pe_final_value).toLocaleString()}</strong></p>
        <p>P/E strategy total return: <strong>${(data.pe_total_return * 100).toFixed(2)}%</strong></p>
    `;

    drawBacktestChart(data.dates, data.values, data.pe_values);
});

function drawBacktestChart(dates, values, peValues) {
    // If there's already a chart from an earlier backtest, remove it first
    if (backtestChart !== null) {
        backtestChart.destroy();
    }

    backtestChart = new Chart(backtestChartCanvas, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Your portfolio',
                    data: values,
                    borderColor: '#1f3a93',
                    pointRadius: 0,
                },
                {
                    label: 'P/E value strategy',      // NEW: the second line
                    data: peValues,
                    borderColor: '#c0392b',
                    pointRadius: 0,
                },
            ],
        },
        options: {
            scales: {
                y: {
                    ticks: {
                        callback: (value) => '$' + value.toLocaleString(),
                    },
                },
            },
        },
    });
}
