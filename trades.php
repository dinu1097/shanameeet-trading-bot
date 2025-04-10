<?php
$brokers = ['ATFX', 'EQUITY', 'EXNESS', 'FXTM', 'ICMarkets', 'XM', 'OANDA', 'Pepperstone', 'FBS', 'OctaFX'];
$stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NFLX', 'NVDA', 'INTC', 'BABA'];

// Generate random prices
$stockPrices = [];
foreach ($stocks as $stock) {
  foreach ($brokers as $broker) {
    $stockPrices[$stock][$broker] = rand(1000, 20000) / 100; // $10.00 to $200.00
  }
}

function simulate_trade($stock, $direction, $stockPrices, $brokers, $startingBroker)
{
  $chain = [];
  $visited = [];

  $currentBroker = $startingBroker;
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

$selectedStock = $stocks[array_rand($stocks)];
$initialBroker = $brokers[array_rand($brokers)];

$longChain = simulate_trade($selectedStock, 'Long', $stockPrices, $brokers, $initialBroker);
$shortChain = simulate_trade($selectedStock, 'Short', $stockPrices, $brokers, $initialBroker);

// Output the table HTML
echo "<table class='min-w-full table-auto border'>";
echo "<thead>
        <tr class='bg-gray-200'>
          <th class='px-4 py-2 border'>Stock</th>
          <th class='px-4 py-2 border'>Direction</th>
          <th class='px-4 py-2 border'>Previous Broker</th>
          <th class='px-4 py-2 border'>Previous Price</th>
          <th class='px-4 py-2 border'>New Broker</th>
          <th class='px-4 py-2 border'>New Price</th>
          <th class='px-4 py-2 border'>Profit %</th>
        </tr>
      </thead>
      <tbody>";

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

echo "</tbody></table>";
?>
