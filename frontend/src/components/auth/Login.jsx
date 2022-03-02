import React, {useEffect, useLayoutEffect} from 'react';
import OktaSignIn from '@okta/okta-signin-widget';
import '@okta/okta-signin-widget/dist/css/okta-sign-in.min.css';
import {useOktaAuth} from "@okta/okta-react";

const Login = () => {
  const authConfig = JSON.parse(sessionStorage.getItem('authConfig'));
  const { oktaAuth } = useOktaAuth();
  let widget;
  useEffect(() => {
    let firstUniqChar = function(s = 'statistics') {
      const letterCounter = {}
      for(const letter of s) {
        console.log(letterCounter, letter, letterCounter[letter])
        if(letterCounter[letter]) {
          letterCounter[letter]++
        }
        else letterCounter[letter] = 1
      }
      for( let i = 0; i < s.length; i++) {
        const stringLetter = s[i]
        console.log(stringLetter)
        if (letterCounter[stringLetter] === 1) {
          return i+1
        }
      }
      return -1
    };
    console.log(firstUniqChar());
    widget = new OktaSignIn({
      el: '#sign-in-widget',
      baseUrl: authConfig.issuer ? authConfig.issuer.split('/oauth2')[0] : '',
      clientId : authConfig.clientId,
      redirectUri : authConfig.redirectUri,
      // logo: authConfig.logo,
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
  }, [oktaAuth]);
  useLayoutEffect(() => {
    return () => {
      try {
        if (widget) {
          widget.remove();
        }
      } catch (e) {}
    }
  },[widget]);
  return (
      <div>
        <div id="sign-in-widget" style={{top: '50px', position: 'relative'}}/>
      </div>
  );
};
export default Login;
