import React, {useEffect} from 'react';
import OktaSignIn from '@okta/okta-signin-widget';
import '@okta/okta-signin-widget/dist/css/okta-sign-in.min.css';
import {useOktaAuth} from "@okta/okta-react";

const Login = () => {
  const authConfig = JSON.parse(sessionStorage.getItem('authConfig'));
  const { oktaAuth } = useOktaAuth();
  useEffect(() => {
    const widget = new OktaSignIn({
      el: '#sign-in-widget',
      baseUrl: authConfig.issuer ? authConfig.issuer.split('/oauth2')[0] : '',
      clientId : authConfig.clientId,
      redirectUri : authConfig.redirectUri,
      logo: '/logo.png',
      authParams: {
        pkce : true,
        issuer : authConfig.issuer,
        responseType: ["token"],
        display: 'page',
        scopes : authConfig.scopes,
      },
    });

    widget.showSignInToGetTokens({
      el: '#sign-in-widget',
      scopes : authConfig.scopes,
    }).then((tokens) => {
      // Add tokens to storage
      oktaAuth.handleLoginRedirect(tokens);
    }).catch((err) => {
      throw err;
    });
  }, [oktaAuth]);

  return (
      <div>
        <div id="sign-in-widget" style={{top: '50px', position: 'relative'}}/>
      </div>
  );
};
export default Login;
