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
  sa = ask.to_i - bid.to_i
  sum = ask.to_i + bid.to_i
  if sum > 100
    if sa > 0
      return 2
    else
      return -2
    end
  elsif sa > 0  && sa < 10
    return 1
  elsif sa > 10 && sa < 60
    return 1.5
  elsif sa > 60
    return 2
  elsif sa < 0 && sa > -10
    return -1
  elsif sa < -10 && sa > -60
    return -1.5
  elsif sa < -60
    return -2
  else
    return 0
  end
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
  puts "買いvol:#{ask}, 売りvol:#{bid}"
  puts "買いvol - 売りvol:#{(ask.to_f - bid.to_f)/1000000}"
  return (ask.to_f - bid.to_f)/1000000
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
    first_price: (price*(1.0+ina)).round,
    first_trigger_price: (price*(1.0+ina)).round-1,
    second_condition_type: "LIMIT", #利確
    second_side: "SELL",
    second_price: (price*((1.0+ina)**2)).ceil,
    third_condition_type: "STOP", #損切り
    third_side: "SELL",
    # third_price: (price*((1.0-ina)**3.5)).ceil-1,
    third_trigger_price: (price*((1.0-ina)**3)).ceil,
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
    first_price: (price*(1.0+ina)).ceil,
    first_trigger_price: (price*(1.0+ina)).ceil+1,
    second_condition_type: "LIMIT",
    second_side: "BUY",
    second_price: (price*((1.0+ina)**2)).round,
    third_condition_type: "STOP",
    third_side: "BUY",
    # third_price: (price*((1.0-ina)**3.5)).ceil+1,
    third_trigger_price: (price*((1.0-ina)**3)).ceil,
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
    first_price: price,
    first_trigger_price: price - 1,
    second_condition_type: "LIMIT", #利確
    second_side: "SELL",
    second_price: price + 30,
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
    first_price: price,
    first_trigger_price: price+1,
    second_condition_type: "LIMIT",
    second_side: "BUY",
    second_price: price-30,
    third_condition_type: "STOP",
    third_side: "BUY",
    # third_price: (price*((1.0-ina)**3.5)).ceil+1,
    third_trigger_price: price+80,
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
j = 0
k = 0
num1, num2 = 0, 0
while true
  if position_size < 0.01 || k == 3
    cancel_loop
    for i in 0..5
      k = 0
      j = 0
      if $client.health["status"] == "NORMAL"
        num1 = inago_sa
        num = num1.abs - num2.abs
        if inago == 2
          if num > 0
            buy_oco(price, inago_sa)
            puts "買い勢い：強 買い特殊注文。"
            puts "1秒待機します。"
            sleep(1)
          else
            buy_oco1(price+50)
            puts "買い勢い：弱 買い特殊注文。"
            puts "3秒待機します。"
            sleep(3)
          end
        elsif inago == 1.5
          buy_oco1(price+20)
          puts "1.5買い特殊注文。"
          puts "3秒待機します。"
          sleep(3)
        elsif inago == 1
          sell_oco1(price-10)
          puts "1売り特殊注文。"
          puts "3秒待機します。"
          sleep(3)
        elsif inago == -2
          if num > 0
            sell_oco(price, inago_sa)
            puts "売り勢い：強 売り特殊注文。"
            puts "1秒待機します。"
            sleep(1)
          else
            sell_oco1(price-50)
            puts "売り勢い：弱 売り特殊注文。"
            puts "3秒待機します。"
            sleep(3)
          end
        elsif inago == -1.5
          sell_oco1(price-20)
          puts "-1.5売り特殊注文。"
          puts "3秒待機します。"
          sleep(3)
        elsif inago == -1
          buy_oco1(price+10)
          puts "-1買い特殊注文。"
          puts "3秒待機します。"
          sleep(3)
        end
        # puts "heikin:#{heikin}, 勢い:#{num*1000000}"
        num2 = num1
      end
    end
  elsif position_length > 0
    if order_length == 0
      puts "予期せぬ建玉があります。"
      cancel
      if position_side == "BUY"
        sell(position_size, price)
        puts "予期せぬ買い建玉を解消しました。"
        sleep(2)
      else
        buy(position_size, price)
        puts "予期せぬ売り建玉を解消しました。"
        sleep(2)
      end
      k += 1
    end
    j += 1
    puts "2秒待機します。"
    sleep(2)
    if j == 5
      puts "約定しないので注文をキャンセルします。"
      cancel_loop
    end
  end
end
# while true
# ina = inago_sa
# puts pre = price
# puts (pre*(1.0+ina)).ceil
# puts (pre*((1.0+ina)**3)).ceil
# puts (pre*((1.0-ina)**2)).ceil
# puts "----------------------------------------"
# sleep(4)
# end
# #---------------------------------------------------------------------------------------------------
