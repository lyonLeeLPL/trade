require "bitflyer_api"
require "pp"
require 'net/http'
require 'uri'
require 'json'

#biflyer api取得----------------------------------------------------
BitflyerApi.configure do |config|
  config.key = "KEY"
  config.secret = "SECRET KEY"
end
client = BitflyerApi.client
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

#買いメソッド、売りメソッド------------------------------------------------------------------------
def buy
  client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "MARKET", side: "BUY", size: 0.1, minute_to_expire: 43200, time_in_force: "GTC")
end

def sell
  client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "MARKET", side: "SELL", size: 0.1, minute_to_expire: 43200, time_in_force: "GTC")
end
# ------------------------------------------------------------------------------------------------

#3分平均線、8分平均線取得関数--------------------------------------------------------------------------
def sen3
time = Time.now.to_i - 120
iti3 = get_json("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc?after=#{time}")['result']['60'].transpose[4]
if iti3.length == 9
  iti3.shift
end
return sen3 = (iti3[0] + 2*iti3[1] + 3*iti3[2])/6
end

def sen8
time = Time.now.to_i - 420
iti8 = get_json("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc?after=#{time}")['result']['60'].transpose[4]
if iti8.length == 9
  iti8.shift
end
return sen8 = (iti8[0] + 2*iti8[1] + 3*iti8[2] + 4*iti8[3] + 5*iti8[4] + 6*iti8[5] + 7*iti8[6] + 8*iti8[7])/36
end
#------------------------------------------------------------------------------------------------

#main---------------------------------------------------------------------------------------------
#平均線の初期値
sen3_before = sen3
sen8_before = sen8
d_before = 0
pos = 0
sleep(60)
#ループ
loop do
  sen3_after = sen3
  sen8_after = sen8
  d_after = sen3_after - sen3_before #傾き
  d = d_after - d_before
  if pos == 0
    if sen3_before < sen8_before && sen3_after > sen8_after #ゴールデンクロス
      buy
      pos = 1
      d_position = d
    elsif sen3_before > sen8_before && sen3_after < sen8_after #デッドクロス
      sell
      pos = -1
      d_position = d
    end
  elsif pos == 1
    if d < d_position
      sell
      pos = 0
    end
  else
    if d > d_position
      buy
      pos = 0
    end
  end
  d_before = d_after
end
