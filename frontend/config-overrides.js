const webpack = require('webpack');
const path = require('path');
const fs = require('fs');

const TESTENV = path.resolve(__dirname, '', 'public/testjson.json');
console.log('PATH', TESTENV);
const env = {}
if (fs.existsSync(TESTENV)) {
  fs.readFile(TESTENV, 'utf8', async function(err, txt) {
    let promise = new Promise((resolve, reject) => {
      if (!err) {
        const jsonData = JSON.parse(txt);
        Object.keys(jsonData).forEach((k) => {
          process.env[k] = jsonData[k];
        });
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
        resolve(env);
      } else {
        reject(err);
      }
    });
    await promise;
  });
} else {
  console.log('There is no path');
}
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