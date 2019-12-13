class Position
  require "./grobal_var"

  #現在のポジションをキャンセル-------------------------------------------------------------------
  def cancel
    while true
      begin
        puts "キャンセルしました。"
        return $client.my_cancel_all_child_orders(product_code: "FX_BTC_JPY")
      break
      rescue => e
        puts "エラーが発生してキャンセルできませんでした。3秒待機します。"
        sleep(3)
      end
    end
  end
  #-----------------------------------------------------------------------------------------------

  #現在のポジションのサイズを取得(volume)------------------------------------------------------------
  def position_size
    while true
      begin
        size = 0.0
        length = $client.my_positions(product_code: "FX_BTC_JPY").length
        for i in 1..length
          size += $client.my_positions(product_code: "FX_BTC_JPY")[i-1]["size"].to_f
        end
        return p size.round(8)
      rescue => e
        puts "エラーが発生してポジションのサイズを取得できませんでした。1秒待機します。"
        p e
        sleep(1)
      end
    end
  end
  #-----------------------------------------------------------------------------------------------

  #現在の注文の量を取得-------------------------------------------------------------------------
  def order_length
    while true
      begin
        return $client.my_child_orders(product_code: "FX_BTC_JPY", count: 100, before: nil, after: nil, child_order_state: nil, child_order_id: nil, child_order_acceptance_id: nil, parent_order_id: nil).length
      rescue => e
        puts "エラーが発生して注文の量を取得できませんでした。1秒待機します。"
        p e
        sleep(1)
      end
    end
  end
  #-----------------------------------------------------------------------------------------------

  #現在のポジションのサイドを取得(BUY or SELL)---------------------------------------------------------
  def position_side
    while true
      begin
      if $client.my_positions(product_code: "FX_BTC_JPY").length > 0
        return $client.my_positions(product_code: "FX_BTC_JPY")[0]['side'] #"SELL" or "BUY"
      else
        return 0
      end
      rescue => e
        puts "エラーが発生してポジションサイドを取得できませんでした。1秒待機します。"
        p e
        sleep(1)
      end
    end
  end
  #-----------------------------------------------------------------------------------------------

  #現在の建て玉の平均値を取得-------------------------------------------------------------------------
  def pos_price
    begin
      return ($client.my_positions(product_code: "FX_BTC_JPY").map{|price| price["price"]}.inject(:+)/$client.my_positions(product_code: "FX_BTC_JPY").length).round
    rescue => e
      puts "エラーが起き、ポジション値段を獲得できませんでした。2秒待機します。"
      sleep(2)
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

end
