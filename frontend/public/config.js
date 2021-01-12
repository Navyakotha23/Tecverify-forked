const CLIENT_ID = '0oauvb74ocd6zt1Yh0h7';
const ISSUER = 'https://tecnics-dev.oktapreview.com/oauth2/ausuvcipegUUQa9Bk0h7'
const MAIN_HEADER = 'TecMFA Bypass Code Generator'
const FRONT_END_URL = "http://localhost:3000";
const BACK_END_URL = "http://localhost:5000";
const AUTHORIZE_TOKEN_TYPE = "idToken";
const AUTHORIZE_CLAIM_NAME = "Admin";
const INSTRUCTIONS_IN_BYPASS_CODE_GENERATOR = [
    'Inform user to click option try another way to open form for entering admin bypass code',
    'Provide the given admin bypass code as generated on the left for respective system'
];
const INSTRUCTIONS_IN_ADMIN_SECRET = [
    'Inform user to click option try another way to open form for entering admin bypass code.'
];

var config = {
    authConfig: {
        clientId: CLIENT_ID,
        issuer: ISSUER,
        redirectUri: `${FRONT_END_URL}/implicit/callback`,
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
    instructionsInAdminSecret: INSTRUCTIONS_IN_ADMIN_SECRET,
    backEndUrl: BACK_END_URL,
    showEncryptedKey: false,
    mainHeader: MAIN_HEADER
};
