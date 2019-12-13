require 'csv'
require 'pp'
$data = CSV.read("ina.csv")
def judge_from_ema
  judgements = Array.new
  pos = 0
  i = 0
  sa = $data.transpose[0].map(&:to_i)
  sa_pre = $data.transpose[1].map(&:to_i)
  price = $data.transpose[2].map(&:to_i)
  # p ema_shorter
  while i < $data.length
    if pos == 0
      if sa[i] > 0 && sa_pre[i] < 0
        judgements << [0.03, 1]
        pos = 1
      elsif sa[i] < 0 && sa_pre[i] > 0
        judgements << [0.03, -1]
        pos = -1
      else
        judgements << [0, 0]
      end
    elsif pos == 1
      if (sa[i] < (sa_pre[i] * 2)) && sa_pre[i] > 100
        judgements << [0.03, -1]
        pos = 0
      elsif sa[i] < 0 && sa_pre[i] > 0
        judgements << [0.06, -1]
        pos = -1
      else
        judgements << [0, 0]
      end
    elsif pos == -1
      if (sa[i] > (sa_pre[i] * 2)) && sa_pre[i] < -100
        judgements << [0.03, 1]
        pos = 0
      elsif sa[i] > 0 && sa_pre[i] < 0
        judgements << [0.06, 1]
        pos = 1
      else
        judgements << [0, 0]
      end
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
price = $data.transpose[2].map(&:to_i)
p judgements = judge_from_ema
#バックテスト．ローソク足の終値で取引すると仮定．最後のローソク足で全てのポジションを決済する．
for i in 0..($data.length - 1)
  if  judgements[i][1] == 1
      total = total - judgements[i][0] * (price[i])
      total1 << total
      position = 1
      number_of_trade += 1
      # puts "#{$data.transpose[4][i+1]}で買い"
  elsif judgements[i][1] == -1
      total = total + judgements[i][0] * (price[i])
      total1 << total
      position = -1
      number_of_trade += 1
  end
end
p position
#最後の足でポジションをまとめて決済．
if position == 1#買いポジを最後に持っていたら売り決済
    total = total + 0.03 * price[-1]
    total1 << total
    position -= 1
    number_of_trade += 1
elsif position == -1#売りポジを最後に持っていたら買い決済
    total = total - 0.03 * price[-1]
    total1 << total
    position += 1
    number_of_trade += 1
    number_of_trade = number_of_trade / 2
end
puts "Trade unit: #{units}"
puts "The position code is #{position} now."
puts "Total P/L per day: #{total-capital}"
puts "The number of trade: #{number_of_trade}"
pp total1
# i = -2
# while total1[i+2] != nil
#   puts total1[i+2]
#   i += 2
# end
