<?php
$brokers = ['ATFX', 'EQUITY', 'EXNESS', 'FXTM', 'ICMarkets', 'XM', 'OANDA', 'Pepperstone', 'FBS', 'OctaFX'];
$stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NFLX', 'NVDA', 'INTC', 'BABA'];

// Check and sanitize input
$type = isset($_POST['type']) ? ($_POST['type'] === 'buy' ? 'BUY' : 'SELL') : null;
$stock = isset($_POST['stock']) && in_array($_POST['stock'], $stocks) ? $_POST['stock'] : null;
$broker = isset($_POST['broker']) && in_array($_POST['broker'], $brokers) ? $_POST['broker'] : null;

if (!$type || !$stock || !$broker) {
  http_response_code(400);
  echo "Invalid trade data";
  exit;
}

// Generate a random price for this stock/broker (simulate current market)
$price = rand(1000, 20000) / 100; // $10.00 - $200.00
$timestamp = date("Y-m-d H:i:s");

// Prepare trade data
$trade = [
  'type' => $type,
  'stock' => $stock,
  'broker' => $broker,
  'price' => $price,
  'time' => $timestamp
];

// Read existing trades
$file = 'data.json';
$existingTrades = file_exists($file) ? json_decode(file_get_contents($file), true) : [];

// Add new trade to the beginning
array_unshift($existingTrades, $trade);

// Keep only the latest 50 trades
$existingTrades = array_slice($existingTrades, 0, 50);

// Save back to file
file_put_contents($file, json_encode($existingTrades, JSON_PRETTY_PRINT));

echo "Trade saved";
