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
  if sa >= 0
    return 1
  else
    return -1
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

#買いメソッド、売りメソッド(li)------------------------------------------------------------------------
def buy_li(price)
  begin
    return p $client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "LIMIT", price: price, side: "BUY", size: 0.01, minute_to_expire: 43200, time_in_force: "GTC")
  rescue => e
    puts "エラーが起き、買えませんでした。2秒待機します。"
    sleep(2)
  end
end

def sell_li(price)
  begin
    return p $client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "LIMIT", price: price, side: "SELL", size: 0.01, minute_to_expire: 43200, time_in_force: "GTC")
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
sa_pre, ikioi_pre = 0, 0
while true
  sa = inago_sa
  ikioi = sa - sa_pre
  ikioi_sa = ikioi - ikioi_pre
  puts "勢い力：#{ikioi_sa}"
  if inago == 1
    if ikioi_sa > 0
      buy_li(price+(ikioi_sa).round)
      puts "買い注文"
    elsif position_size >= 0.01
      cancel_loop
      if position_side == "BUY"
        sell_ma(position_size)
        puts "買い決済"
      else
        buy_ma(position_size)
        puts "売り決済"
      end
    end
  elsif inago == -1
    if ikioi_sa < 0
      sell_li(price-(ikioi_sa).round)
      puts "売り注文"
    elsif position_size >= 0.01
      cancel_loop
      if position_side == "BUY"
        sell_ma(position_size)
        puts "買い決済"
      else
        buy_ma(position_size)
        puts "売り決済"
      end
    end
  end
  sleep(5)
  ikioi_pre = ikioi
  sa_pre = sa
  cancel_loop
end
# #---------------------------------------------------------------------------------------------------
