const CLIENT_ID = '0oauvb74ocd6zt1Yh0h7';
const ISSUER = 'https://tecnics-dev.oktapreview.com/oauth2/ausuvcipegUUQa9Bk0h7'
const AUTHORIZE_TOKEN_TYPE = "idToken";
const AUTHORIZE_CLAIM_NAME = "Admin";
const INSTRUCTIONS_IN_BYPASS_CODE_GENERATOR = [
  '1. Inform user to click option try another way to open form for entering admin bypass code',
  '2. Provide the given admin bypass code as generated on the left for respective system'
];
const INSTRUCTIONS_IN_ADMIN_SECRET = [
  '1. Inform user to click option try another way to open form for entering admin bypass code.'
];

export default {
  authConfig: {
    clientId: CLIENT_ID,
    issuer: ISSUER,
    redirectUri: 'http://localhost:3000/implicit/callback',
    scopes: [
      'openid',
      'email',
      'tecmfa'
    ],
    pkce: true,
    disableHttpsCheck: false
  },
  authorizeTokenType: AUTHORIZE_TOKEN_TYPE,
  authorizeClaimName: AUTHORIZE_CLAIM_NAME,
  instructionsInBypassCodeGenerator: INSTRUCTIONS_IN_BYPASS_CODE_GENERATOR,
  instructionsInAdminSecret: INSTRUCTIONS_IN_ADMIN_SECRET
};