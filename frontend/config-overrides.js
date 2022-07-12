const path = require('path');
const fs = require('fs');

const TESTENV = path.resolve(__dirname, '', 'public/config/app.config.json');
console.log('PATH', TESTENV);
if (fs.existsSync(TESTENV)) 
{
    console.log('Path found', TESTENV);
} else 
{
  console.log('There is no path');
}