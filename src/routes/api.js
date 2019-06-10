import {elasticClient, generateElasticQuery} from '@lib/elastic'
import {co} from '@lib/util'

export default (fastify, options, next) => {
  fastify.get(
    '/healthcheck',
    co(function * (req, res) {
      return 'ALIVE'
    }),
  )
  // TODO: use redis for cache... to allow scaling past 1 process
  fastify.register(require('fastify-rate-limit'), {
    max: 1,
    timeWindow: 2000,
  })
  fastify.get(
    '/search',
    co(function * (req, res) {
      const searchResult = yield elasticClient.search({
        index: process.env.INDEX_NAME,
        body: generateElasticQuery(req.query),
      })
      // not sure if this works
      return searchResult.body.hits.hits.map(x => x['_source'])
    }),
  )
  next()
}