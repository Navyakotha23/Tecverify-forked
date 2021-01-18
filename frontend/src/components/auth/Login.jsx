import React, {useEffect, useRef} from 'react';
import OktaSignIn from '@okta/okta-signin-widget';
import '@okta/okta-signin-widget/dist/css/okta-sign-in.min.css';
import {useOktaAuth} from "@okta/okta-react";
import config from "../../config";

const Login = () => {
  const authConfig = {
    clientId: config.authConfig.clientId,
    disableHttpsCheck: config.authConfig.disableHttpsCheck,
    issuer: config.authConfig.issuer,
    pkce: config.authConfig.pkce,
    redirectUri: config.authConfig.redirectUri,
    scopes: config.authConfig.scopes.split(',')
  };
  const { oktaAuth } = useOktaAuth();

  useEffect(() => {
    const widget = new OktaSignIn({
      el: '#sign-in-widget',
      baseUrl: authConfig.issuer ? authConfig.issuer.split('/oauth2')[0] : '',
      clientId : authConfig.clientId,
      redirectUri : authConfig.redirectUri,
      logo: '/logo.png',
      authParams: {
        pkce : authConfig.pkce,
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

    return () => widget.remove();
  }, [oktaAuth]);

  return (
      <div>
        <div id="sign-in-widget" style={{top: '50px', position: 'relative'}}/>
      </div>
  );
};
export default Login;
