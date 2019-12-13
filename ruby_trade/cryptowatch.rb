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
    lowprice = ary[4]
  end
  average += (ary[2] + ary[3])/2
end

average = average/30
longprice = lowprice + (average - lowprice)/3
shortprice = highprice - (highprice - average)/3
p a.length
p highprice
p lowprice
p average
p shortprice
p longprice
