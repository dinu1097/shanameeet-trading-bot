<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Broker Trade Tracker</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>

<body class="bg-gray-100 p-6">
  <div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-4">Broker Trade Tracker</h1>

    <!-- Manual Trade Form -->
    <div class="bg-white shadow-md rounded p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">Simulate a Trade</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label for="stock" class="block font-medium mb-1">Select Stock</label>
          <select id="stock" class="w-full border rounded p-2">
            <option value="AAPL">AAPL</option>
            <option value="GOOGL">GOOGL</option>
            <option value="MSFT">MSFT</option>
            <option value="AMZN">AMZN</option>
            <option value="TSLA">TSLA</option>
            <option value="META">META</option>
            <option value="NFLX">NFLX</option>
            <option value="NVDA">NVDA</option>
            <option value="INTC">INTC</option>
            <option value="BABA">BABA</option>
          </select>
        </div>
        <div>
          <label for="broker" class="block font-medium mb-1">Select Broker</label>
          <select id="broker" class="w-full border rounded p-2">
            <option value="ATFX">ATFX</option>
            <option value="EQUITY">EQUITY</option>
            <option value="EXNESS">EXNESS</option>
            <option value="FXTM">FXTM</option>
            <option value="ICMarkets">ICMarkets</option>
            <option value="XM">XM</option>
            <option value="OANDA">OANDA</option>
            <option value="Pepperstone">Pepperstone</option>
            <option value="FBS">FBS</option>
            <option value="OctaFX">OctaFX</option>
          </select>
        </div>
        <div class="flex items-end gap-2">
          <button onclick="fakeTrade('buy')" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded">Buy</button>
          <button onclick="fakeTrade('sell')" class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded">Sell</button>
        </div>
      </div>
    </div>

    <!-- Live Trade Display -->
    <div class="bg-white shadow-md rounded p-6">
      <h2 class="text-xl font-semibold mb-4">Trade Transitions (Live)</h2>
      <div id="table-container">
        <!-- Table will be loaded via JS -->
      </div>
    </div>
  </div>

  <script>
    async function fetchTrades() {
      const response = await fetch('trades2.php');
      const html = await response.text();
      document.getElementById('table-container').innerHTML = html;
    }

    function fakeTrade(type) {
      const stock = document.getElementById('stock').value;
      const broker = document.getElementById('broker').value;

      fetch('simulate_trade.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `type=${type}&stock=${stock}&broker=${broker}`
      }).then(fetchTrades);
    }

    fetchTrades();
    setInterval(fetchTrades, 3000); // Auto-refresh
  </script>
</body>

</html>
