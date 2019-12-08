class Inago
  #イナゴ取得----------------------------------------------------------
  def inago
    ask = String.new
    bid = String.new
    $driver.find_elements(:id, "buyVolumePerMeasurementTime").each do |buyvol|
    	ask = buyvol.text
    end
    $driver.find_elements(:id, "sellVolumePerMeasurementTime").each do |sellvol|
    	bid = sellvol.text
    end
    sa = (ask.to_i - bid.to_i).abs
    if sa >= 150
      return 1
    else
      return -1
    end
  end
  #--------------------------------------------------------------------
end
