require 'csv'
require 'pp'
$data = CSV.read("ina1.csv")
def judge_from_ema
  judgements = Array.new
  pos = 0
  i = 0
  sa_pos = 0
  pos_size = 0
  volume = 0.01
  ask = $data.transpose[0].map(&:to_i)
  bid = $data.transpose[1].map(&:to_i)
  ask_bid = $data.transpose[2].map(&:to_i)
  sa = $data.transpose[3].map(&:to_i)
  sa_pre = $data.transpose[4].map(&:to_i)
  price = $data.transpose[5].map(&:to_i)
  price_sa = $data.transpose[6].map(&:to_i)
  # p ema_shorter
  while i < $data.length
    if (pos == 1 && ask[i] <= bid[i]) || (pos_size >= 0.5 && pos == 1)
      judgements << [pos_size.round(4), -1]
      pos_size = 0
      pos = 0
    elsif (pos == -1 && ask[i] >= bid[i]) || (pos_size >= 0.5 && pos == -1)
      judgements << [pos_size.round(4), 1]
      pos_size = 0
      pos = 0
    elsif ((pos == 0) || (pos == 1)) && ask[i] >= bid[i]+1
      judgements << [volume, 1]
      pos_size += volume
      pos = 1
    elsif ((pos == 0) || (pos == -1)) && ask[i]+1 <= bid[i]
      judgements << [volume, -1]
      pos_size += volume
      pos = -1
    end
    i += 1
  end
  return judgements
end


capital = 0
total = capital
#取引単位（BTC）
units = 0.1
total1 = Array.new
total1[0] = total

#買いポジを持っているときは1，売りポジを持っているときは-1，ポジを持っていないときは0
position = 0
number_of_trade = 0
price = $data.transpose[5].map(&:to_i)
p judgements = judge_from_ema
#バックテスト．ローソク足の終値で取引すると仮定．最後のローソク足で全てのポジションを決済する．
for i in 0..(judgements.length - 1)
  if  judgements[i][1] == 1
      total = total - judgements[i][0] * (price[i])
      total1 << total
      position += judgements[i][0]
      number_of_trade += 1
      # puts "#{$data.transpose[4][i+1]}で買い"
  elsif judgements[i][1] == -1
      total = total + judgements[i][0] * (price[i])
      total1 << total
      position -= judgements[i][0]
      number_of_trade += 1
  end
end
p position = position.round(4)
#最後の足でポジションをまとめて決済．
if position > 0#買いポジを最後に持っていたら売り決済
    total = total + position * price[-1]
    total1 << total
    position -= position
    number_of_trade += 1
elsif position < 0#売りポジを最後に持っていたら買い決済
    total = total + position * price[-1]
    total1 << total
    position -= position
    number_of_trade += 1
    number_of_trade = number_of_trade / 2
end
# pp total1
puts "Trade unit: #{units}"
puts "The position code is #{position} now."
puts "Total P/L per day: #{total-capital}"
puts "The number of trade: #{number_of_trade}"
# i = -2
# while total1[i+2] != nil
#   puts total1[i+2]
#   i += 2
# end
