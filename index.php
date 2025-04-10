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
      <h2 class="text-xl font-semibold mb-4">Trade Transitions</h2>
      <table class="min-w-full table-auto border">
        <thead>
          <tr class="bg-gray-200">
            <th class="px-4 py-2 border">Stock</th>
            <th class="px-4 py-2 border">Direction</th>
            <th class="px-4 py-2 border">Previous Broker</th>
            <th class="px-4 py-2 border">Previous Price</th>
            <th class="px-4 py-2 border">New Broker</th>
            <th class="px-4 py-2 border">New Price</th>
            <th class="px-4 py-2 border">Profit %</th>
          </tr>
        </thead>
        <tbody>
          <?php
          $brokers = ['ATFX', 'EQUITY', 'EXNESS', 'FXTM', 'ICMarkets', 'XM', 'OANDA', 'Pepperstone', 'FBS', 'OctaFX'];
          $stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NFLX', 'NVDA', 'INTC', 'BABA'];

          $stockPrices = [];
          foreach ($stocks as $stock) {
            foreach ($brokers as $broker) {
              $stockPrices[$stock][$broker] = rand(1000, 20000) / 100;
            }
          }

          function simulate_trade($stock, $direction, $stockPrices, $brokers)
          {
            $chain = [];
            $visited = [];

            $currentBroker = $brokers[array_rand($brokers)];
            $currentPrice = $stockPrices[$stock][$currentBroker];
            $visited[] = $currentBroker;

            while (true) {
              $foundBetter = false;
              foreach ($brokers as $broker) {
                if (in_array($broker, $visited)) continue;

                $price = $stockPrices[$stock][$broker];
                if (
                  ($direction === 'Long' && $price < $currentPrice) ||
                  ($direction === 'Short' && $price > $currentPrice)
                ) {
                  $profit = abs(($price - $currentPrice) / $currentPrice) * 100;
                  $chain[] = [
                    'stock' => $stock,
                    'direction' => $direction,
                    'prevBroker' => $currentBroker,
                    'prevPrice' => $currentPrice,
                    'newBroker' => $broker,
                    'newPrice' => $price,
                    'profit' => number_format($profit, 2)
                  ];
                  $currentBroker = $broker;
                  $currentPrice = $price;
                  $visited[] = $broker;
                  $foundBetter = true;
                  break;
                }
              }
              if (!$foundBetter) break;
            }

            return $chain;
          }

          $longStock = $stocks[array_rand($stocks)];
          $shortStock = $stocks[array_rand($stocks)];

          $longChain = simulate_trade($longStock, 'Long', $stockPrices, $brokers);
          $shortChain = simulate_trade($shortStock, 'Short', $stockPrices, $brokers);

          foreach (array_merge($longChain, $shortChain) as $trade) {
            echo "<tr class='text-center'>";
            echo "<td class='border px-4 py-2'>{$trade['stock']}</td>";
            echo "<td class='border px-4 py-2'>{$trade['direction']}</td>";
            echo "<td class='border px-4 py-2'>{$trade['prevBroker']}</td>";
            echo "<td class='border px-4 py-2'>\$" . number_format($trade['prevPrice'], 2) . "</td>";
            echo "<td class='border px-4 py-2'>{$trade['newBroker']}</td>";
            echo "<td class='border px-4 py-2'>\$" . number_format($trade['newPrice'], 2) . "</td>";
            echo "<td class='border px-4 py-2 text-green-600 font-bold'>{$trade['profit']}%</td>";
            echo "</tr>";
          }
          ?>
        </tbody>
      </table>
    </div>
  </div>
</body>

</html>
