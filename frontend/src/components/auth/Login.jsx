import React, { useEffect } from 'react';
import OktaSignIn from '@okta/okta-signin-widget';
import '@okta/okta-signin-widget/dist/css/okta-sign-in.min.css';

const Login = () => {
  const config = window.config;

  useEffect(() => {
    const { pkce, issuer, clientId, redirectUri, scopes } = config.authConfig;
    const widget = new OktaSignIn({
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
    widget.renderEl(
      { el: '#sign-in-widget' },
      () => {},
      (err) => {
        throw err;
      },
    );
  }, []);

  return (
      <div>
        <div id="sign-in-widget" style={{marginTop: '15px'}}/>
      </div>
  );
};
export default Login;
