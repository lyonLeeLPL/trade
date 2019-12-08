class MovingAverage
  require "./grobal_var"
  require "./Ita"

  attr_accessor :genbutu, :btcfx, :kairi, :sfd_5

  def initialize
  end


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
end
