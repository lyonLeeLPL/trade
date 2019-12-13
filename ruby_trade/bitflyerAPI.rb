class BitFlyerAPI
  require "bitflyer_api"
  require "pp"

  def initialize(key, secret)
    @key = key
    @secret = secret
  end

  BitflyerApi.configure do |config|
    config.key = @key
    config.secret = @secret
  end

  client = BitflyerApi.client

  def health
    p client.health["status"]
  end
end
