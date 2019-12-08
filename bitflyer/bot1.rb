require "bitflyer_api"
require "pp"

BitflyerApi.configure do |config|
  config.key = "KEY"
  config.secret = "SECRET KEY"
end

client = BitflyerApi.client

require 'net/http'
require 'uri'
require 'json'
require 'pp'

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

loop do
  highprice = 0
  lowprice = 1000000
  average = 0
  count = 0

  time = Time.now.to_i - 1740
  a = get_json("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc?after=#{time}")['result']['60']

  if a.length == 31
    a.pop
  end
  a.each do |ary|
    if highprice < ary[2]
      highprice = ary[2]
    end
    if lowprice > ary[3]
      lowprice = ary[3]
    end
    average += (ary[2] + ary[3])/2
  end

  average = average/30
  longprice = lowprice + (average - lowprice)/3
  shortprice = highprice - (highprice - average)/3
  #指値注文
  if client.my_positions(product_code: "FX_BTC_JPY").length == 0
    loop do
      highprice = 0
      lowprice = 1000000
      average = 0

      time = Time.now.to_i - 1740
      a = get_json("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc?after=#{time}")['result']['60']

      if a.length == 31
        a.pop
      end
      a.each do |ary|
        if highprice < ary[2]
          highprice = ary[2]
        end
        if lowprice > ary[3]
          lowprice = ary[3]
        end
        average += (ary[2] + ary[3])/2
      end

      average = average/30
      longprice = lowprice + (average - lowprice)/3
      shortprice = highprice - (highprice - average)/3

      if (client.board(product_code: "FX_BTC_JPY")['mid_price'] > longprice) && (client.board(product_code: "FX_BTC_JPY")['mid_price'] < shortprice)
        if highprice - lowprice < 5000
          if client.health['status'] == "NORMAL"
            count += 1
            client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "LIMIT", side: "BUY", price: longprice, size: 0.1, minute_to_expire: 43200, time_in_force: "GTC")
            client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "LIMIT", side: "SELL", price: shortprice, size: 0.1, minute_to_expire: 43200, time_in_force: "GTC")
            puts "#{count}：#{longprice}でロング指値、#{shortprice}でショート指値"
            puts "平均価格：#{average} 最高価格：#{highprice} 最低価格：#{lowprice} 現在の価格：#{client.board(product_code: "FX_BTC_JPY")['mid_price']}"
            break
          end
        end
      end
    end
  end

  #片方の注文をキャンセル
  loop do
    if client.my_positions(product_code: "FX_BTC_JPY").length > 0
      sleep(1)
      if client.my_positions(product_code: "FX_BTC_JPY") != []
        if client.my_positions(product_code: "FX_BTC_JPY")[0]['side'] == "SELL"
          puts "ショート"
        else
          puts "ロング"
        end
        client.my_cancel_all_child_orders(product_code: "FX_BTC_JPY")
        puts "片方の指値をキャンセルしました。"
        break
      end
    end
  end


  loop do
    if client.health['status'] == "NORMAL"
      if client.my_positions(product_code: "FX_BTC_JPY")[0]['side'] == "BUY"
        if (client.board(product_code: "FX_BTC_JPY")['mid_price'] > average) || (client.board(product_code: "FX_BTC_JPY")['mid_price'] < lowprice)
          client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "MARKET", side: "SELL", price: nil, size: 0.1, minute_to_expire: 43200, time_in_force: "GTC")
          puts "#{client.board(product_code: "FX_BTC_JPY")['mid_price']-longprice}yen\n"
          sleep(1)
          break
        end
      else
        if (client.board(product_code: "FX_BTC_JPY")['mid_price'] < average) || (client.board(product_code: "FX_BTC_JPY")['mid_price'] > highprice)
          client.my_send_child_order(product_code: "FX_BTC_JPY", child_order_type: "MARKET", side: "BUY", price: nil, size: 0.1, minute_to_expire: 43200, time_in_force: "GTC")
          puts "#{shortprice-client.board(product_code: "FX_BTC_JPY")['mid_price']}yen\n"
          sleep(1)
          break
        end
      end
    end
  end
end
