class Sfd
  require "pp"
  require "./grobal_var"

  attr_accessor :genbutu, :btcfx, :kairi, :sfd_5

  def initialize
    @genbutu = nil
    @btcfx = nil
    @kairi = nil
    @sfd_5 = nil
  end

  #BTC現物価格、FX価格, 現在の乖離率、SFD比率取得---------------------------
  def sfd_price
    p @genbutu = $client.board(product_code: "BTC_JPY")['mid_price']
    p @btcfx = $client.board(product_code: "FX_BTC_JPY")['mid_price']
    p @kairi = ((@btcfx / @genbutu) - 1) * 100
    return p @sfd_5 = (@genbutu * 1.05).round
  end
  #-------------------------------------------------------------------
end
