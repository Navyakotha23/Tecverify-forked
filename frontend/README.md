This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`


Now you need to gather the following information from the Okta Developer Console:

- **Client Id** - The client ID of the SPA application that you created earlier. This can be found on the "General" tab of an application, or the list of applications.  This identifies the application that tokens will be minted for.
- **Issuer** - This is the URL of the authorization server that will perform authentication.  All Developer Accounts have a "default" authorization server.  The issuer is a combination of your Org URL (found in the upper right of the console home page) and `/oauth2/default`. For example, `https://dev-1234.oktapreview.com/oauth2/default`.


These values must exist as environment variables. They can be exported in the shell, or saved in a file named `testenv`, at the root of this repository. (This is the parent directory, relative to this README) See [dotenv](https://www.npmjs.com/package/dotenv) for more details on this file format.

```
ISSUER=https://yourOktaDomain.com/oauth2/default
CLIENT_ID=123xxxxx123
SCOPES='email,username,profile'
MAIN_HEADER = 'HEADER'
FRONT_END_URL = "http://localhost:3000"
BACK_END_URL = "http://localhost:5000"
AUTHORIZE_TOKEN_TYPE = "idToken"
AUTHORIZE_CLAIM_NAME = "Admin"
INSTRUCTIONS_IN_BYPASS_CODE_GENERATOR = "xxxxxx,xxxxxx,xxxxx"   // instructions seperated with ','
INSTRUCTIONS_IN_ADMIN_SECRET = "xxxxxx,xxxxxx,xxxxx"   // instructions seperated with ','
SHOW_ENCRYPTED_KEY = "false"
```

With variables set, start the app server:


Runs the app in the development mode.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br />
You will also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.<br />

### `npm run build`

Builds the app for production to the `build` folder.<br />
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br />
Your app is ready to be deployed!
