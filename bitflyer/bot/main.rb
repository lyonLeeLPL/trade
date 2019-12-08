require "bitflyer_api"
require "pp"
require 'net/http'
require 'uri'
require 'json'
require 'selenium-webdriver'

require "./Trade"
require "./Sfd"
require "./grobal_var"
require "./Position"
require "./Inago"
require "./Ita"

#注文遅延削除-----------------------------------------------------------------
def tien
  i = 0
  while position_size >= 0.01
    puts "注文が遅延しています。5秒待機します。"
    sleep(5)
    i += 1
    if i == 1
      puts "注文が消えました。"
      cancel
      break
    end
  end
end

def tien1
  i = 0
  while position_size < 0.01
    puts "注文が遅延しています。5秒待機します。"
    sleep(5)
    i += 1
    if i == 1
      puts "注文が消えました。"
      cancel
      break
    end
  end
end

#main-------------------------------------------------------------------------------------------
sfd = Sfd.new
trade = Trade.new
pos = Position.new

trade.sell_li(sfd.sfd_price, 0.01)
sleep(5)
if pos.position_size > 0
  trade.buy_li(sfd.sfd_price-1, 0.01)
else
  pos.cancel
end

# #---------------------------------------------------------------------------------------------------
