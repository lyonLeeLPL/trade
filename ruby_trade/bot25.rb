require "bitflyer_api"
require "pp"
require 'net/http'
require 'uri'
require 'json'
require 'selenium-webdriver'

options = Selenium::WebDriver::Chrome::Options.new
options.add_argument('--headless')
$driver = Selenium::WebDriver.for :chrome, options: options
$driver.get("https://inagoflyer.appspot.com/btcmac")

#イナゴ取得----------------------------------------------------------
def inago
  ask = String.new
  bid = String.new
  $driver.find_elements(:id, "buyVolumePerMeasurementTime").each do |buyvol|
  	ask = buyvol.text
  end
  $driver.find_elements(:id, "sellVolumePerMeasurementTime").each do |sellvol|
  	bid = sellvol.text
  end
  sa = (ask.to_i - bid.to_i).abs
  if sa >= 150
    return 1
  else
    return -1
  end
end
#--------------------------------------------------------------------


#biflyer api取得----------------------------------------------------
BitflyerApi.configure do |config|
  config.key = 'KEY'
  config.secret = 'SECRET KEY'
end
$client = BitflyerApi.client
#-------------------------------------------------------------------

#json取得関数---------------------------------------------------------------------------------
def get_json(location, limit = 10)
  raise ArgumentError, 'too many HTTP redirects' if limit == 0
  uri = URI.parse(location)
  begin
    response = Net::HTTP.start(uri.host, uri.port, use_ssl: uri.scheme == 'https') do |http|
      http.open_timeout = 5
      http.read_timeout = 10
      http.get(uri.request_uri)
    end
    case response
    when Net::HTTPSuccess
      json = response.body
      JSON.parse(json)
    when Net::HTTPRedirection
      location = response['location']
      warn "redirected to #{location}"
      get_json(location, limit - 1)
    else
      puts [uri.to_s, response.value].join(" : ")
      # handle error
    end
  rescue => e
    puts [uri.to_s, e.class, e].join(" : ")
    # handle error
  end
end
#----------------------------------------------------------------------------------------------

#現在の値を取得----------------------------------------------------------------------------------
def price
  while true
    begin
      # time = Time.now.to_i
      # price = get_json("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc?after=#{time}")['result']['60'].transpose[4]
      # return price[-1]
      return $client.board(product_code: "FX_BTC_JPY")['mid_price'].round
     rescue => e
      puts "エラーで価格が取得できませんでした。3秒待機します。"
      sleep(3)
    end
  end
end
#-----------------------------------------------------------------------------------------------

#買いメソッド、売りメソッド(li)------------------------------------------------------------------------
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
# ------------------------------------------------------------------------------------------------

#買いメソッド、売りメソッド(ma)------------------------------------------------------------------------
def buy_ma(volume)
  while true
    begin
      return p $client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "MARKET", side: "BUY", size: volume, minute_to_expire: 43200, time_in_force: "GTC")
    rescue => e
      puts "エラーが起き、買えませんでした。2秒待機します。"
      sleep(2)
    end
  end
end

def sell_ma(volume)
  while true
    begin
      return p $client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "MARKET", side: "SELL", size: volume, minute_to_expire: 43200, time_in_force: "GTC")
    rescue => e
      puts "エラーが起き、買えませんでした。2秒待機します"
      sleep(2)
    end
  end
end
# ------------------------------------------------------------------------------------------------

#現在のポジションを取得-------------------------------------------------------------------------
def position_length
  while true
    begin
      return $client.my_positions(product_code: "FX_BTC_JPY").length
    rescue => e
      puts "エラーが発生してポジション数を取得できませんでした。3秒待機します。"
      sleep(3)
    end
  end
end
#-----------------------------------------------------------------------------------------------

#現在のポジションをキャンセル-------------------------------------------------------------------
def cancel
  while true
    begin
      puts "キャンセルしました。"
      return $client.my_cancel_all_child_orders(product_code: "FX_BTC_JPY")
    break
    rescue => e
      puts "エラーが発生してキャンセルできませんでした。3秒待機します。"
      sleep(3)
    end
  end
end
#-----------------------------------------------------------------------------------------------

#現在の出来高の正負を取得----------------------------------------------------------------------------------
def dekidaka
  while true
    begin
      time = Time.now.to_i
      price = get_json("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc?after=#{time}")['result']['60']
      return price[-1][1] - price[-1][4]
     rescue => e
      puts "エラーで価格が取得できませんでした。3秒待機します。"
      sleep(3)
    end
  end
end
#-----------------------------------------------------------------------------------------------

#現在のポジションのサイズを取得(volume)-------------------------------------------------------------------------
def position_size
  while true
    begin
      size = 0.0
      length = $client.my_positions(product_code: "FX_BTC_JPY").length
      for i in 1..length
        size += $client.my_positions(product_code: "FX_BTC_JPY")[i-1]["size"].to_f
      end
      return p size.round(8)
    rescue => e
      puts "エラーが発生してポジションのサイズを取得できませんでした。1秒待機します。"
      p e
      sleep(1)
    end
  end
end
#-----------------------------------------------------------------------------------------------

#現在の注文の量を取得-------------------------------------------------------------------------
def order_length
  while true
    begin
      return $client.my_child_orders(product_code: "FX_BTC_JPY", count: 100, before: nil, after: nil, child_order_state: nil, child_order_id: nil, child_order_acceptance_id: nil, parent_order_id: nil).length
    rescue => e
      puts "エラーが発生して注文の量を取得できませんでした。1秒待機します。"
      p e
      sleep(1)
    end
  end
end
#-----------------------------------------------------------------------------------------------

#現在のポジションのサイドを取得-------------------------------------------------------------------------
def position_side
  while true
    begin
    if $client.my_positions(product_code: "FX_BTC_JPY").length > 0
      return $client.my_positions(product_code: "FX_BTC_JPY")[0]['side'] #"SELL" or "BUY"
    else
      return 0
    end
    rescue => e
      puts "エラーが発生してポジションサイドを取得できませんでした。1秒待機します。"
      p e
      sleep(1)
    end
  end
end
#-----------------------------------------------------------------------------------------------

#現在の約定平均価格を取得-----------------------------------------------------------------
def heikin
  while true
    begin
      time = Time.now.to_i
      a = get_json("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/trades?limit=30")
      goukei = 0
      for i in 0..29
        goukei += a['result'][i][2]
      end
      return (goukei)/30
     rescue => e
      return
      puts "エラーで価格が取得できませんでした。3秒待機します。"
      puts e
      sleep(3)
    end
  end
end
#-----------------------------------------------------------------------------------------------
#キャンセルループ-----------------------------------------------------------------
def cancel_loop
  i = 0
  while order_length != 0
    cancel
    puts "キャンセルしました。"
    i += 1
    if i == 10
      break
    end
  end
end
#-----------------------------------------------------------------------------------------------

#注文遅延削除-----------------------------------------------------------------
def tien
  i = 0
  while position_size >= 0.01
    puts "注文が遅延しています。5秒待機します。"
    sleep(5)
    i += 1
    if i == 1
      puts "注文が消えました。"
      cancel
      break
    end
  end
end

def tien1
  i = 0
  while position_size < 0.01
    puts "注文が遅延しています。5秒待機します。"
    sleep(5)
    i += 1
    if i == 1
      puts "注文が消えました。"
      cancel
      break
    end
  end
end

def orderbuy(buyprice, rikakuprice, stopprice, volume, volume1)
  begin
    if volume == 0
      volume = 0.01 if volume == nil
      volume1 = 0.01 if volume1 == nil
      volume = 0.01 if volume == 0
      volume1 = 0.01 if volume1 == 0
      p $client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "LIMIT", price: rikakuprice, side: "SELL", size: volume1, minute_to_expire: 43200, time_in_force: "GTC")
      p $client.my_send_parent_order(
      order_method: "SIMPLE",
      minute_to_expire: 43200,
      time_in_force: "GTC",
      product_code: "FX_BTC_JPY",
      first_condition_type: "STOP",
      first_side: "SELL",
      # first_price: stopprice,
      first_trigger_price: stopprice,
      size: volume1,
      offset: nil
      )
    elsif volume1 == 0
      volume = 0.01 if volume == nil
      volume1 = 0.01 if volume1 == nil
      volume = 0.01 if volume == 0
      volume1 = 0.01 if volume1 == 0
      p $client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "LIMIT", price: buyprice, side: "BUY", size: volume, minute_to_expire: 43200, time_in_force: "GTC")
    else
      volume = 0.01 if volume == nil
      volume1 = 0.01 if volume1 == nil
      volume = 0.01 if volume == 0
      volume1 = 0.01 if volume1 == 0
      p $client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "LIMIT", price: buyprice, side: "BUY", size: volume, minute_to_expire: 43200, time_in_force: "GTC")
      p $client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "LIMIT", price: rikakuprice, side: "SELL", size: volume1, minute_to_expire: 43200, time_in_force: "GTC")
      p $client.my_send_parent_order(
      order_method: "SIMPLE",
      minute_to_expire: 43200,
      time_in_force: "GTC",
      product_code: "FX_BTC_JPY",
      first_condition_type: "STOP",
      first_side: "SELL",
      # first_price: stopprice,
      first_trigger_price: stopprice,
      size: volume1,
      offset: nil
      )
    end
  rescue => e
    puts "エラーが起き、買えませんでした。2秒待機します。"
    sleep(2)
  end
end
def ordersell(sellprice, rikakuprice, stopprice, volume, volume1)
  begin
    if volume == 0
      volume = 0.01 if volume == nil
      volume1 = 0.01 if volume1 == nil
      volume = 0.01 if volume == 0
      volume1 = 0.01 if volume1 == 0
      p $client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "LIMIT", price: rikakuprice, side: "BUY", size: volume1, minute_to_expire: 43200, time_in_force: "GTC")
      p $client.my_send_parent_order(
      order_method: "SIMPLE",
      minute_to_expire: 43200,
      time_in_force: "GTC",
      product_code: "FX_BTC_JPY",
      first_condition_type: "STOP",
      first_side: "BUY",
      # first_price: stopprice,
      first_trigger_price: stopprice,
      size: volume1,
      offset: nil
      )
    elsif volume1 == 0
      volume = 0.01 if volume == nil
      volume1 = 0.01 if volume1 == nil
      volume = 0.01 if volume == 0
      volume1 = 0.01 if volume1 == 0
      p $client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "LIMIT", price: sellprice, side: "SELL", size: volume, minute_to_expire: 43200, time_in_force: "GTC")
    else
      volume = 0.01 if volume == nil
      volume1 = 0.01 if volume1 == nil
      volume = 0.01 if volume == 0
      volume1 = 0.01 if volume1 == 0
      p $client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "LIMIT", price: sellprice, side: "SELL", size: volume, minute_to_expire: 43200, time_in_force: "GTC")
      p $client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "LIMIT", price: rikakuprice, side: "BUY", size: volume1, minute_to_expire: 43200, time_in_force: "GTC")
      p $client.my_send_parent_order(
      order_method: "SIMPLE",
      minute_to_expire: 43200,
      time_in_force: "GTC",
      product_code: "FX_BTC_JPY",
      first_condition_type: "STOP",
      first_side: "BUY",
      # first_price: stopprice,
      first_trigger_price: stopprice,
      size: volume1,
      offset: nil
      )
    end
  rescue => e
    puts "エラーが起き、買えませんでした。2秒待機します。"
    sleep(2)
  end
end

def pos_price
  begin
    return ($client.my_positions(product_code: "FX_BTC_JPY").map{|price| price["price"]}.inject(:+)/$client.my_positions(product_code: "FX_BTC_JPY").length).round
  rescue => e
    puts "エラーが起き、ポジション値段を獲得できませんでした。2秒待機します。"
    sleep(2)
  end
end
#-----------------------------------------------------------------------------------------------


#main-------------------------------------------------------------------------------------------
i, j = 0, 0
pos = 0
# while true
best_ask, best_bid, mid_price = 0
while true
  sell = 0
  buy = 0
  ary = $client.ticker(product_code: "FX_BTC_JPY")
  best_bid = ary["best_bid"].round
  best_ask = ary["best_ask"].round
  p sa = (best_ask - best_bid)
  mid_price = (best_bid + best_ask)/2
  p bid_size_5 = $client.board(product_code: "FX_BTC_JPY")["bids"].take(30).map{|item| item["size"]}.inject(:+)
  p ask_size_5 = $client.board(product_code: "FX_BTC_JPY")["asks"].take(30).map{|item| item["size"]}.inject(:+)
  size_ask = 0
  pri_ask = 0
  $client.board(product_code: "FX_BTC_JPY")["asks"].take(30).map do |item|
    if size_ask < item["size"]
      size_ask = item["size"]
      pri_ask = item["price"].round
    end
  end
  size_bid = 0
  pri_bid = 0
  $client.board(product_code: "FX_BTC_JPY")["bids"].take(30).map do |item|
    if size_bid < item["size"]
      size_bid = item["size"]
      pri_bid = item["price"].round
    end
  end
  # size_asks = 0
  # multi_asks = 0
  # $client.board(product_code: "FX_BTC_JPY")["asks"].take(10).map do |item|
  #   if size_asks < item["size"]
  #     size_asks = item["size"]
  #     multi_asks = item["price"].round
  #   end
  # end
  # size_bids = 0
  # multi_bids = 0
  # $client.board(product_code: "FX_BTC_JPY")["bids"].take(10).map do |item|
  #   if size_bids < item["size"]
  #     size_bids = item["size"]
  #     multi_bids = item["price"].round
  #   end
  # end
  puts size_ask
  puts size_bid
  puts pri_ask
  puts pri_bid
  cancel
  if position_size <= 0.01
    if (bid_size_5 > ask_size_5) && size_ask > 3
      orderbuy(mid_price, pri_ask-1, pri_bid-1, 0.02, 0.02)
      puts "買い指値"
    elsif (bid_size_5 < ask_size_5) && size_bid > 3
      ordersell(mid_price, pri_bid+1, pri_ask+1, 0.02, 0.02)
      puts "売り指値"
    end
    i += 1
  end
  if position_size >= 0.01
    if position_side == "BUY"
      if bid_size_5 > ask_size_5
        orderbuy(mid_price, pri_ask-1, pri_bid-1, 0, (position_size).round(4))
        puts "買い指値1"
      else
        ordersell(mid_price, pri_bid+1, pri_ask+1, (position_size).round(4), 0)
        puts "売り指値1"
      end
    elsif position_side == "SELL"
      if bid_size_5 > ask_size_5
        orderbuy(mid_price, pri_ask-1, pri_bid-1, (position_size).round(4), 0)
        puts "買い指値2"
      else
        ordersell(mid_price, pri_bid+1, pri_ask+1, 0, (position_size).round(4))
        puts "売り指値2"
      end
    end
    i += 1
  end
  sleep(5)
  puts "------------------------"
  if inago == 1
    cancel
    if position_side == "SELL"
      buy_ma(position_size)
    elsif position_side == "BUY"
      sell_ma(position_size)
    end
  end
end
# #---------------------------------------------------------------------------------------------------
