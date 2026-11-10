/*
AI DISCLOSURE: THE ENTIRE FILE (app.js) WAS WRITTEN BY AI (Claude).
None of the javascript below is my own work. At least, not anymore; I had the hello world test before LOL.
I did not write any of these lines. What I did do was decide what the page needed to do, and connect it to my 
Python backend (app.py). The comments in this file are my explanation of what each part does, so that I understand 
the code.

Layout of this file (please keep in mind, every section is AI written):
    1. Stock list; fills the page with a checkbox and amount box for each stock
    2. Portfolio panel; the sticky box that shows the saved portfolio
    3. Stock search; filters the stock list as the user types
    4. Save portfolio; sends the chosen stocks to /api/portfolio
    5. Step 2: Hedge; asks /api/hedge for the best hedging stock
    6. Reset portfolio; clears the page and /api/portfolio/reset
    7. Step 3: Optimise; sends the target risk to /api/optimise
    8. Step 4: Backtest; date pickers, results text and the animated chart
*/


//[AI WRITTEN] 1. Stock list
async function loadStockList() { //asks the backend for every stock the user can pick, and adds a row for each one to the page
    const response = await fetch('/api/stocks'); //ask app.py for the list (the get_stocks route)
    const data = await response.json();
    const stockListDiv = document.getElementById('stock_list');

    for (const stock of data.stocks) { //for each stock:
        const row = document.createElement('div');
        row.className = 'stock-row';
        row.innerHTML = `
            <label><input type="checkbox" class="stock-checkbox" value="${stock}"> ${stock}</label>
            $<input type="number" class="stock_amount" id="amount-${stock}" min="5000" step="1000" placeholder="Amount">
        `; //a checkbox to pick the stock, and a box to type how many dollars to put in it (min $5000)
        stockListDiv.appendChild(row);
    }
}

loadStockList(); //run it as soon as the page loads

// [AI WRITTEN] 2. Sticky portfolio panel
const portfolioPanelBody = document.getElementById('portfolio_panel_body');

async function refreshPortfolioPanel() { //redraws the sticky panel with whatever portfolio is currently saved. Called after every save/reset/optimise.
    const response = await fetch('/api/portfolio/current'); //the current_portfolio route in app.py
    const data = await response.json();

    if (data.holdings.length === 0) {
        portfolioPanelBody.innerHTML = '<p>No stocks yet. Pick some in Step 1.</p>'; //nothing saved yet
        return;
    }

    let html = '<table><tr><th>Stock</th><th>Weight</th><th>Value</th></tr>'; //start a table
    for (const row of data.holdings) { //one table row for each stock in the portfolio
        html += `<tr>
            <td>${row.Stock}</td>
            <td>${(row.Weight * 100).toFixed(1)}%</td>
            <td>$${Math.round(row.Value).toLocaleString()}</td>
        </tr>`; //weight is turned into a percentage, and the value is rounded and given commas
    }
    html += `</table>
        <p>Invested: <strong>$${Math.round(data.invested).toLocaleString()}</strong><br>
        Cash left: <strong>$${Math.round(data.cash_left).toLocaleString()}</strong></p>`; //totals under the table
    portfolioPanelBody.innerHTML = html;
}

refreshPortfolioPanel(); //show the saved portfolio as soon as the page loads


// [AI WRITTEN] 3. Search for a stock 
const stockSearch = document.getElementById('stock_search');
const stockSearchMessage = document.getElementById('stock_search_message');

stockSearch.addEventListener('input', () => { //runs every time the user types in the search box
    const query = stockSearch.value.trim().toLowerCase(); //what they typed, ignoring spaces and capitals
    let shown = 0; //counts how many stocks match

    for (const row of document.querySelectorAll('.stock-row')) {
        const symbol = row.querySelector('.stock-checkbox').value.toLowerCase();
        const matches = symbol.includes(query);   // empty search matches everything
        row.hidden = !matches; //hide the rows that don't match
        if (matches) shown++;
    }

    stockSearchMessage.textContent = shown === 0 ? 'No stocks match your search.' : ''; //tell the user if nothing matched
});

//  [AI WRITTEN] 4. Save portfolio 
const saveButton = document.getElementById('save_portfolio_button');
const saveMessage = document.getElementById('save_portfolio_message');

saveButton.addEventListener('click', async () => { //when the user clicks save
    // 1. Build a list of the stocks the user ticked
    const holdings = [];
    const checkboxes = document.querySelectorAll('.stock-checkbox');

    for (const checkbox of checkboxes) {
        if (checkbox.checked) {
            const stock = checkbox.value;
            const amount = Number(document.getElementById(`amount-${stock}`).value); //the dollar amount typed next to that stock
            holdings.push({ stock: stock, value: amount });
        }
    }

    // 2. Send it to Python
    const response = await fetch('/api/portfolio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ portfolio: holdings }),
    }); //this is the save_portfolio route in app.py, which does the checking
    const data = await response.json();

    // 3. Show Python's reply
    if (!response.ok) { //app.py sent back an error (e.g. under $5000, or over the starting capital)
        portfolioMessage.textContent = data.error;
        return;
    }
    saveMessage.textContent = `${data.message} Cash left: $${data.cash_left.toLocaleString()}`;
    refreshPortfolioPanel();
});


//  [AI WRITTEN] 5. Step 2: Find a hedge 
const hedgeButton = document.getElementById('hedge_portfolio_button');
const hedgeMessage = document.getElementById('hedge_portfolio_message');

hedgeButton.addEventListener('click', async () => {
    hedgeMessage.textContent = 'Calculating...'; //shown while waiting, as hedge() can take a moment

    const response = await fetch('/api/hedge'); //the hedge_portfolio route, which calls hedge() in hedging.py
    const data = await response.json();

    hedgeMessage.textContent = `The best stock to hedge your portfolio is ${data.stock_recommendation} (covariance: ${data.covariance_value.toFixed(6)})`;
});

//  [AI WRITTEN] 6. Reset portfolio 
const resetButton = document.getElementById('reset_portfolio_button');

resetButton.addEventListener('click', async () => {
    // 0. Double-check, since this deletes their portfolio
    if (!confirm('Are you sure you want to reset your portfolio?')) {
        return;
    }

    // 1. Clear the page
    for (const checkbox of document.querySelectorAll('.stock-checkbox')) {
        checkbox.checked = false; //untick every stock
    }
    for (const amountBox of document.querySelectorAll('.stock-amount')) {
        amountBox.value = ''; //empty every amount box
    }
    hedgeMessage.textContent = '';

    // 2. Clear the saved file
    const response = await fetch('/api/portfolio/reset', { method: 'POST' }); //the reset_portfolio route in app.py
    const data = await response.json();
    saveMessage.textContent = data.message;
    refreshPortfolioPanel();
});



//  [AI WRITTEN] 7. Step 3: Optimise 
const riskInput = document.getElementById('risk_range_input');
const optimiseButton = document.getElementById('optimise_portfolio_button');
const optimiseMessage = document.getElementById('optimise_portfolio_message');
const optimisedPortfolioDiv = document.getElementById('optimised_portfolio');

optimiseButton.addEventListener('click', async () => {
    const risk = Number(riskInput.value); //the yearly risk the user wants, e.g. 0.15 is 15%
    if (risk <= 0) {
        optimiseMessage.textContent = 'Please enter a target risk, e.g. 0.15 for 15% yearly volatility.';
        return;
    }

    optimiseMessage.textContent = 'Optimising...';
    optimisedPortfolioDiv.innerHTML = ''; //clear the old result

    const response = await fetch('/api/optimise', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ yearly_risk: risk }),
    }); //the optimise_portfolio route, which calls run_optimisation() in optimiser.py
    const data = await response.json();

    if (!response.ok) { //e.g. fewer than 2 stocks, or no portfolio can reach that low a risk
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
    refreshPortfolioPanel();
});



//  [AI WRITTEN] 8. Step 4: Backtest 
const backtestStartInput = document.getElementById('backtest_start_date');
const backtestEndInput = document.getElementById('backtest_end_date');
const backtestButton = document.getElementById('backtest_button');
const backtestMessage = document.getElementById('backtest_message');
const backtestResults = document.getElementById('backtest_results');
const backtestChartCanvas = document.getElementById('backtest_chart');
const backtestDateRangeMessage = document.getElementById('backtest_date_range_message');
let backtestChart = null;      // holds the chart once it's drawn
const backtestProgress = document.getElementById('backtest_progress');
const ANIMATION_MS = 8000;          // total time for a long backtest
let backtestAnimation = null;       // id of the running animation frame


async function loadBacktestDateRange() { //finds the earliest and latest dates we have data for, and sets up the two date pickers with them
    const response = await fetch('/api/backtest/date-range'); //the backtest_date_range route in app.py
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

backtestButton.addEventListener('click', async () => { //when the user clicks run backtest
    backtestMessage.textContent = 'Running backtest...';
    backtestResults.innerHTML = '';

    const response = await fetch('/api/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            start_date: backtestStartInput.value,
            end_date: backtestEndInput.value,
        }),
    }); //the backtest_portfolio route, which calls run_backtest() in backtest.py
    const data = await response.json();

    if (!response.ok) { //e.g. bad dates, or an empty portfolio
        backtestMessage.textContent = data.error;
        return;
    }
    backtestMessage.textContent = '';

    drawBacktestChart(data.dates, data.values, data.pe_values, () => showBacktestResults(data)); //draw the chart, and only show the results text once the animation is done
});

function showBacktestResults(data) { //writes the final numbers (value, returns, years) under the chart
    backtestResults.innerHTML = `
        <p>Final portfolio value: <strong>$${Math.round(data.final_portfolio_value).toLocaleString()}</strong></p>
        <p>Total return: <strong>${(data.total_return * 100).toFixed(2)}%</strong></p>
        <p>Backtest period: <strong>${data.years.toFixed(2)} years</strong></p>
        <p>Average annual return: <strong>${(data.average_annual_return * 100).toFixed(2)}%</strong></p>
        <p>P/E strategy final value: <strong>$${Math.round(data.pe_final_value).toLocaleString()}</strong></p>
        <p>P/E strategy total return: <strong>${(data.pe_total_return * 100).toFixed(2)}%</strong></p>
    `;
}


function drawBacktestChart(dates, values, peValues, onFinish) { //draws the two lines (my portfolio vs the P/E strategy) week by week, as an animation, using the Chart.js library
    // Stop any animation still running, and remove the old chart
    if (backtestAnimation !== null) {
        cancelAnimationFrame(backtestAnimation);
        backtestAnimation = null;
    }
    if (backtestChart !== null) {
        backtestChart.destroy();
    }

    // Fix the y-axis from ALL the data, so it doesn't rescale as the lines grow
    const allValues = values.concat(peValues);
    const yMin = Math.min(...allValues);
    const yMax = Math.max(...allValues);

    backtestChart = new Chart(backtestChartCanvas, {
        type: 'line',
        data: {
            labels: dates,                       // full x-axis from the start
            datasets: [
                { label: 'Your portfolio',    data: [], borderColor: '#1f3a93', pointRadius: 0 },
                { label: 'P/E value strategy', data: [], borderColor: '#c0392b', pointRadius: 0 },
            ], //both lines start empty, and get filled in week by week below
        },
        options: {
            animation: false,                    // we drive the animation ourselves
            scales: {
                y: {
                    min: yMin * 0.95,
                    max: yMax * 1.05,
                    ticks: { callback: (value) => '$' + value.toLocaleString() },
                },
            },
        },
    });

    const totalWeeks = dates.length;
    const msPerWeek = Math.min(100, ANIMATION_MS / totalWeeks); //long backtests are sped up so the whole thing takes about 8 seconds
    const startTime = performance.now();

    function step(now) { //runs once per frame, and reveals a few more weeks each time
        // how many weeks should be visible by now?
        const shown = Math.min(totalWeeks, Math.floor((now - startTime) / msPerWeek) + 1);

        backtestChart.data.datasets[0].data = values.slice(0, shown); //only give the chart the first 'shown' weeks
        backtestChart.data.datasets[1].data = peValues.slice(0, shown);
        backtestChart.update('none');            // redraw with no built-in animation

        const i = shown - 1;
        backtestProgress.textContent =
            `Week ${shown} of ${totalWeeks} (${dates[i]}): ` +
            `your portfolio $${Math.round(values[i]).toLocaleString()}, ` +
            `P/E strategy $${Math.round(peValues[i]).toLocaleString()}`;

        if (shown < totalWeeks) {
            backtestAnimation = requestAnimationFrame(step); //not finished, so do another frame
        } else {
            backtestAnimation = null;
            if (onFinish) onFinish(); //finished, so show the results text
        }
    }
    backtestAnimation = requestAnimationFrame(step);
}
