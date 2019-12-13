require "bitflyer_api"
require "pp"
require 'csv'

BitflyerApi.configure do |config|
  config.key = 'KEY'
  config.secret = 'SECRET KEY'
end

client = BitflyerApi.client
$id = String.new

CSV.open('test.csv','a') do |test|
  client.my_executions(product_code: 'FX_BTC_JPY', count: 500, before: nil, after: nil, child_order_id: nil, child_order_acceptance_id: nil).each do |a|
    $id = a['id']
    a['side'] = "売り" if a['side'] == 'SELL'
    a['side'] = "買い" if a['side'] == 'BUY'
    test << [1, 1, 1, 1, a['side'], a['size'], 1, a['price'].round, a['exec_date']]
  end
  for i in 0..10
    client.my_executions(product_code: 'FX_BTC_JPY', count: 500, before: $id, after: nil, child_order_id: nil, child_order_acceptance_id: nil).each do |a|
      $id = a['id']
      a['side'] = "売り" if a['side'] == 'SELL'
      a['side'] = "買い" if a['side'] == 'BUY'
      test << [1, 1, 1, 1, a['side'], a['size'], 1, a['price'].round, a['exec_date']]
    end
  end
end
