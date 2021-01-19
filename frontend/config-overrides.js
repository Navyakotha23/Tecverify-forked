const path = require('path');
const dotenv = require('dotenv');
const fs = require('fs');

const TESTENV = path.resolve(__dirname, '..', 'testenv');
console.log('PATH', TESTENV);
if (fs.existsSync(TESTENV)) {
  console.log('ENV config', fs.readFileSync(TESTENV));
  const envConfig = dotenv.parse(fs.readFileSync(TESTENV));
  Object.keys(envConfig).forEach((k) => {
    process.env[k] = envConfig[k];
  });
} else {
  console.log('There is no path');
}
process.env.CLIENT_ID = process.env.CLIENT_ID || process.env.SPA_CLIENT_ID;

const webpack = require('webpack');

const env = {};

[
  'ISSUER',
  'CLIENT_ID',
  'SCOPES',
  'MAIN_HEADER',
  'FRONT_END_URL',
  'BACK_END_URL',
  'AUTHORIZE_TOKEN_TYPE',
  'AUTHORIZE_CLAIM_NAME',
  'INSTRUCTIONS_IN_BYPASS_CODE_GENERATOR',
  'INSTRUCTIONS_IN_ADMIN_SECRET',
  'SHOW_ENCRYPTED_KEY'
].forEach((key) => {
  if (!process.env[key]) {
    throw new Error(`Environment variable ${key} must be set. See README.md`);
  }
  env[key] = JSON.stringify(process.env[key]);
});

module.exports = {
  webpack: (config) => {
    config.resolve.plugins = [];
    config.plugins = config.plugins.concat([
      new webpack.DefinePlugin({
        'process.env': env,
      }),
    ]);
    config.devtool = 'source-map';
    config.module.rules.push({
      test: /\.js$/,
      use: ['source-map-loader'],
      enforce: 'pre',
    });
    return config;
  },
};
