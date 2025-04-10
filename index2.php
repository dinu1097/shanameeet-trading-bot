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
    <div class="bg-white shadow-md rounded p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">Trade Transitions (Live)</h2>
      <div id="table-container">
        <!-- Trade table will be injected here -->
      </div>
    </div>
  </div>

  <script>
    async function fetchTrades() {
      const response = await fetch('trades.php');
      const html = await response.text();
      document.getElementById('table-container').innerHTML = html;
    }

    fetchTrades();
    setInterval(fetchTrades, 3000); // Refresh every 3 seconds
  </script>
</body>

</html>
