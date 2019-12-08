require 'csv'
require 'pp'
$data = CSV.read("btc_3.csv")
short_ema = Array.new
middle_ema = Array.new
#日時、始値、高値、安値、終値
last_price = $data.transpose[4].map(&:to_i)
last_price.each_cons(4) do |a, b, c, d|
  short_ema << (a + 2*b + 3*c + 4*d)/10
end
last_price.each_cons(8) do |a, b, c, d, e, f, g, h|
  middle_ema << (a + 2*b + 3*c + 4*d + 5*e + 6*f + 7*g + 8*h)/36
end
for i in 0..3
short_ema.shift
end
for i in 0..6
$data.shift
end
# p short_ema.length
# p $data.length
# p middle_ema.length
def judge_from_ema(ema_shorter, ema_longer)
  judgements = [0]*$data.length
  pos = 0
  ema3_before = ema_shorter[0]
  ema8_before = ema_longer[0]
  d_previous = 0
  d8 = 0
  i = 0
  j = $data.length
  # p ema_shorter
  while i < j-1
    ema3_after = ema_shorter[i]
    ema8_after = ema_longer[i]
    d3 = ema3_after - ema3_before #傾き
    d8 = ema8_after - ema8_before
    # a = d3 - d8
    if pos == 0
      if d3 > d3*0.01 && d8 > d8*0.01
        judgements[i] = 1
        pos = 1
        d_position = d3
      elsif d3 < d3*0.01 && d8 < d8*0.01
        judgements[i] = -1
        pos = -1
        d_position = d3
      end
    elsif pos == 1
      if d3 < d_previous
        judgements[i] = -1
        pos =0
      else
        judgements[i] = 0
      end
    else
      if d3 > d_previous
        judgements[i] = 1
        pos = 0
      else
        judgements[i] = 0
      end
    end
    d_previous = d3
    ema8_before = ema_longer[i]
    ema3_before = ema_shorter[i]
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
judgements = judge_from_ema(short_ema, middle_ema)

#バックテスト．ローソク足の終値で取引すると仮定．最後のローソク足で全てのポジションを決済する．
for i in 0..($data.length - 1)
  if  judgements[i] == 1
      total = total - units * $data.transpose[4][i].to_i
      total1 << total
      position += 1
      number_of_trade += 1
      # puts "#{$data.transpose[4][i+1]}で買い"
  elsif judgements[i] == -1
      total = total + units * $data.transpose[4][i].to_i
      total1 << total
      position -= 1
      number_of_trade += 1
  end
end

#最後の足でポジションをまとめて決済．
if position == 1#買いポジを最後に持っていたら売り決済
    total = total + units * $data.transpose[4][-1].to_i
    total1 << total
    position -= 1
    number_of_trade += 1
elsif position == -1#売りポジを最後に持っていたら買い決済
    total = total - units * $data[-1][4].to_i
    total1 << total
    position += 1
    number_of_trade += 1
    number_of_trade = number_of_trade / 2
end
puts "Trade unit: #{units}"
puts "The position code is #{position} now."
puts "Total P/L per day: #{total-capital}"
puts "The number of trade: #{number_of_trade}"
i = -2
while total1[i+2] != nil
  puts total1[i+2]
  i += 2
end
