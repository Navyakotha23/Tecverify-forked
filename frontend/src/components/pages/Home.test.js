import React from 'react';
import Home from './Home';
import { shallow } from 'enzyme';

// jest.mock("../auth/Login", () => {
//     return <div>SignInWidgetMock</div>;
// });

jest.mock('@okta/okta-react', () => ({
    useOktaAuth: () => {
        return {
            authState: {},
            authService: {getUser: () => Promise.resolve({email: 'qweqwe', Admin: true})}
        };
    }
}));

const CLIENT_ID = '0oauvb74ocd6zt1Yh0h7';
const ISSUER = 'https://tecnics-dev.oktapreview.com/oauth2/ausuvcipegUUQa9Bk0h7'
const MAIN_HEADER = 'TecMFA Bypass Code Generator'
const FRONT_END_URL = "http://localhost:3000";
const BACK_END_URL = "http://localhost:5000";
const AUTHORIZE_TOKEN_TYPE = "idToken";
const AUTHORIZE_CLAIM_NAME = "Admin";
const INSTRUCTIONS_IN_BYPASS_CODE_GENERATOR = [
    '1. Inform user to click option try another way to open form for entering admin bypass code',
    '2. Provide the given admin bypass code as generated on the left for respective system'
];
const INSTRUCTIONS_IN_ADMIN_SECRET = [
    '1. Inform user to click option try another way to open form for entering admin bypass code.'
];

var config = {
    authConfig: {
        clientId: CLIENT_ID,
        issuer: ISSUER,
        redirectUri: `${FRONT_END_URL}/implicit/callback`,
        scopes: [
            'openid',
            'email'
        ],
        pkce: true,
        disableHttpsCheck: false
    },
    authorizeTokenType: AUTHORIZE_TOKEN_TYPE,
    authorizeClaimName: AUTHORIZE_CLAIM_NAME,
    instructionsInBypassCodeGenerator: INSTRUCTIONS_IN_BYPASS_CODE_GENERATOR,
    instructionsInAdminSecret: INSTRUCTIONS_IN_ADMIN_SECRET,
    backEndUrl: BACK_END_URL,
    mainHeader: MAIN_HEADER
};

beforeEach(() => {
    window.config = { ...config };
});

describe('MyComponent', () => {
    test('works with withAuth()', done => {
        const wrapper = shallow(Home);
        setImmediate(() => {
            wrapper.update();
            try {
                /* Make your assertions here */
                done();
            } catch (error) {
                done.fail(error);
            }
        });
    });
});