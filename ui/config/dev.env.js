'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')


module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  API_ENDPOINT: process.env.API_URL//'"http://172.17.0.1:5000/captcha22/api/v1.0/"'
})