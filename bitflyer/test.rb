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
  return [ask.to_i, bid.to_i, ask.to_i+bid.to_i]
end
#--------------------------------------------------------------------

#イナゴ取得----------------------------------------------------------
def inago_sa
  ask = String.new
  bid = String.new
  $driver.find_elements(:id, "buyVolumePerMeasurementTime").each do |buyvol|
  	ask = buyvol.text
  end
  $driver.find_elements(:id, "sellVolumePerMeasurementTime").each do |sellvol|
  	bid = sellvol.text
  end
  # puts "買いvol:#{ask}, 売りvol:#{bid}"
  # puts "買いvol - 売りvol:#{(ask.to_f - bid.to_f)}"
  return (ask.to_f - bid.to_f)
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

#IFDOCO注文----------------------------------------------------------------------------------
def buy_oco(price, ina)
  begin
    return p $client.my_send_parent_order(
    order_method: "IFDOCO",
    minute_to_expire: 43200,
    time_in_force: "GTC",
    product_code: "FX_BTC_JPY",
    first_condition_type: "STOP_LIMIT",
    first_side: "BUY",
    first_price: (price+ina/2).round,
    first_trigger_price: (price+ina/2).round-1,
    second_condition_type: "LIMIT", #利確
    second_side: "SELL",
    second_price: (price+ina).round,
    third_condition_type: "STOP", #損切り
    third_side: "SELL",
    # third_price: (price*((1.0-ina)**3.5)).ceil-1,
    third_trigger_price: (price-ina/2).round,
    size: 0.02,
    offset: nil
    )
    rescue => e
      p e
     puts "エラーが発生してロングポジションを取得できませんでした。"
   end
end

def sell_oco(price, ina)
  begin
    return p $client.my_send_parent_order(
    order_method: "IFDOCO",
    minute_to_expire: 43200,
    time_in_force: "GTC",
    product_code: "FX_BTC_JPY",
    first_condition_type: "STOP_LIMIT",
    first_side: "SELL",
    first_price: (price-ina/2).round,
    first_trigger_price: (price-ina/2).round+1,
    second_condition_type: "LIMIT",
    second_side: "BUY",
    second_price: (price-ina).round,
    third_condition_type: "STOP",
    third_side: "BUY",
    # third_price: (price*((1.0-ina)**3.5)).ceil+1,
    third_trigger_price: (price+ina/2).round,
    size: 0.02,
    offset: nil
    )
  rescue => e
    p e
   puts "エラーが発生してショートポジションを取得できませんでした。"
 end
end
#------------------------------------------------------------------------------------------------------------

#IFDOCO注文----------------------------------------------------------------------------------
def buy_oco1(price)
  begin
    return p $client.my_send_parent_order(
    order_method: "IFDOCO",
    minute_to_expire: 43200,
    time_in_force: "GTC",
    product_code: "FX_BTC_JPY",
    first_condition_type: "STOP_LIMIT",
    first_side: "BUY",
    first_price: price+20,
    first_trigger_price: price+19,
    second_condition_type: "LIMIT", #利確
    second_side: "SELL",
    second_price: price+50,
    third_condition_type: "STOP", #損切り
    third_side: "SELL",
    # third_price: (price*((1.0-ina)**3.5)).ceil-1,
    third_trigger_price: price - 40,
    size: 0.04,
    offset: nil
    )
    rescue => e
      p e
     puts "エラーが発生してロングポジションを取得できませんでした。"
   end
end

def sell_oco1(price)
  begin
    return p $client.my_send_parent_order(
    order_method: "IFDOCO",
    minute_to_expire: 43200,
    time_in_force: "GTC",
    product_code: "FX_BTC_JPY",
    first_condition_type: "STOP_LIMIT",
    first_side: "SELL",
    first_price: price-20,
    first_trigger_price: price-19,
    second_condition_type: "LIMIT",
    second_side: "BUY",
    second_price: price-50,
    third_condition_type: "STOP",
    third_side: "BUY",
    # third_price: (price*((1.0-ina)**3.5)).ceil+1,
    third_trigger_price: price+40,
    size: 0.04,
    offset: nil
    )
  rescue => e
    p e
   puts "エラーが発生してショートポジションを取得できませんでした。"
 end
end
#------------------------------------------------------------------------------------------------------------

#買いメソッド、売りメソッド------------------------------------------------------------------------
def buy(volume, price)
  while true
    begin
      return p $client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "MARKET", side: "BUY", size: volume, minute_to_expire: 43200, time_in_force: "GTC")
    rescue => e
      puts "エラーが起き、買えませんでした。2秒待機します。"
      sleep(2)
    end
  end
end

def sell(volume, price)
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
      return size.round(8)
    rescue => e
      puts "エラーが発生してポジションのサイズを取得できませんでした。3秒待機します。"
      p e
      sleep(3)
    end
  end
end
#-----------------------------------------------------------------------------------------------

#現在の注文の量を取得-------------------------------------------------------------------------
def order_length
  while true
    begin
      return $client.my_parent_orders(product_code: "FX_BTC_JPY", count: 100, before: nil, after: nil, parent_order_state: "ACTIVE").length
    rescue => e
      puts "エラーが発生して注文の量を取得できませんでした。3秒待機します。"
      p e
      sleep(3)
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
      puts "エラーが発生してポジションサイドを取得できませんでした。3秒待機します。"
      p e
      sleep(3)
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
  while order_length == 0
    puts "注文が遅延しています。3秒待機します。"
    sleep(3)
    i += 1
    if i == 30
      puts "注文が消えました。"
      break
    end
  end
end
#-----------------------------------------------------------------------------------------------


#main-------------------------------------------------------------------------------------------
require "csv"
a1, a2, price1, price_pre = 0, 0, 0, 0
ary = Array.new
while true
ary= inago
a1 = inago_sa.round
price1 = price
CSV.open('ina1.csv','a') do |ina|
 ina << [ary[0],ary[1],ary[2],a1,a2,price1,price1-price_pre]
end
puts "ask:#{ary[0]}: bid:#{ary[1]} ask+bid:#{ary[2]}差：#{a1} 前の差:#{a2} 値段：#{price1} 値段の差：#{price1 - price_pre}"
sleep(5)
a2 = a1
price_pre = price1

end
# # #---------------------------------------------------------------------------------------------------
