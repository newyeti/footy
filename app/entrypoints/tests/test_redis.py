import redis
import certifi

r = redis.Redis(
  host='gusc1-sought-glider-30297.upstash.io',
  port=30297,
  password='948ad8cff81847d2a5f4daeaad30906f',
  ssl=True,
  ssl_cert_reqs="none"
)

r.set('foo', 'bar')
print(r.get('foo'))


