class Ita
  require "./Position"
  require "./grobal_var"
  require "bitflyer_api"
  require "pp"
  require 'net/http'
  require 'uri'
  require 'json'
  require 'selenium-webdriver'


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
end
