import React, {useEffect, useRef} from 'react';
import OktaSignIn from '@okta/okta-signin-widget';
import '@okta/okta-signin-widget/dist/css/okta-sign-in.min.css';
import {useOktaAuth} from "@okta/okta-react";

const Login = () => {
  const config = window.config;
  const { oktaAuth } = useOktaAuth();
  const { pkce, issuer, clientId, redirectUri, scopes } = config.authConfig;

  useEffect(() => {
    const widget = new OktaSignIn({
      el: '#sign-in-widget',
      baseUrl: issuer ? issuer.split('/oauth2')[0] : '',
      clientId,
      redirectUri,
      logo: '/logo.png',
      authParams: {
        pkce,
        issuer,
        responseType: ["token"],
        display: 'page',
        scopes,
      },
    });

    widget.showSignInToGetTokens({
      el: '#sign-in-widget',
      scopes,
    }).then((tokens) => {
      // Add tokens to storage
      oktaAuth.handleLoginRedirect(tokens);
    }).catch((err) => {
      throw err;
    });

    return () => widget.remove();
  }, [oktaAuth]);

  return (
      <div>
        <div id="sign-in-widget" style={{top: '50px', position: 'relative'}}/>
      </div>
  );
};
export default Login;
