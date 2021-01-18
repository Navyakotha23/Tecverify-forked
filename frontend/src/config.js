const CLIENT_ID = process.env.CLIENT_ID || '';
const ISSUER = process.env.ISSUER || '';
const SCOPES = process.env.SCOPES || '';
const MAIN_HEADER = process.env.MAIN_HEADER || '';
const FRONT_END_URL = process.env.FRONT_END_URL || '';
const BACK_END_URL = process.env.BACK_END_URL || '';
const AUTHORIZE_TOKEN_TYPE = process.env.AUTHORIZE_TOKEN_TYPE || '';
const AUTHORIZE_CLAIM_NAME = process.env.AUTHORIZE_CLAIM_NAME || '';
const INSTRUCTIONS_IN_BYPASS_CODE_GENERATOR = process.env.INSTRUCTIONS_IN_BYPASS_CODE_GENERATOR || '';
const INSTRUCTIONS_IN_ADMIN_SECRET = process.env.INSTRUCTIONS_IN_ADMIN_SECRET || '';
const SHOW_ENCRYPTED_KEY = process.env.SHOW_ENCRYPTED_KEY || false;

export default {
  authConfig: {
    clientId: CLIENT_ID,
    issuer: ISSUER,
    redirectUri: `${FRONT_END_URL}/implicit/callback`,
    scopes: SCOPES,
    pkce: true,
    disableHttpsCheck: false,
  },
  authorizeTokenType: AUTHORIZE_TOKEN_TYPE,
  authorizeClaimName: AUTHORIZE_CLAIM_NAME,
  instructionsInBypassCodeGenerator: INSTRUCTIONS_IN_BYPASS_CODE_GENERATOR,
  instructionsInAdminSecret: INSTRUCTIONS_IN_ADMIN_SECRET,
  backEndUrl: BACK_END_URL,
  showEncryptedKey: SHOW_ENCRYPTED_KEY,
  mainHeader: MAIN_HEADER
};
