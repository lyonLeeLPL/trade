class Trade
  require "pp"
  require "./grobal_var"

  def buy_li(price, volume)
    begin
      return p $client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "LIMIT", price: price, side: "BUY", size: volume, minute_to_expire: 43200, time_in_force: "GTC")
    rescue => e
      puts "エラーが起き、買えませんでした。2秒待機します。"
      sleep(2)
    end
  end

  def sell_li(price, volume)
    begin
      return p $client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "LIMIT", price: price, side: "SELL", size: volume, minute_to_expire: 43200, time_in_force: "GTC")
    rescue => e
      puts "エラーが起き、買えませんでした。2秒待機します"
      sleep(2)
    end
  end

end

trade = Trade.new
trade.price
