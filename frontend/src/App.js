import React from 'react';
import { BrowserRouter as Router, Route, useHistory } from 'react-router-dom';
import { Security, SecureRoute, LoginCallback } from '@okta/okta-react';
import Login from './components/auth/Login';
import { OktaAuth } from '@okta/okta-auth-js'
import Home from './components/pages/Home';
import Dashboard from './components/pages/dashboard';
import config from "./config";

const HasAccessToRouter = () => {
    const authConfig = {
        clientId: config.authConfig.clientId,
        disableHttpsCheck: config.authConfig.disableHttpsCheck,
        issuer: config.authConfig.issuer,
        pkce: config.authConfig.pkce,
        redirectUri: config.authConfig.redirectUri,
        scopes: config.authConfig.scopes.split(',')
    };
    const oktaAuth = new OktaAuth(authConfig);
    const history = useHistory();
    const customAuthHandler = () => {
    history.push('/login');
    };
    if(typeof authConfig === "object") {
        return (
            <Security
                oktaAuth={oktaAuth}
                onAuthRequired={customAuthHandler}
            >
                <Route path="/" exact component={Dashboard} />
                <SecureRoute path="/home" exact component={Home} />
                <Route path="/implicit/callback" component={LoginCallback} />
                <Route path="/login" exact component={Login} />
            </Security>
        );
    } else {
        return (<div className="popup-box" style={{background: '#ffffff50'}}>
            <div className="config-error-box">
                <div style={{background: '#ff4949', height: '50px', padding: '10px'}}>
                    <h2>Alert</h2>
                </div>
                <p style={{fontSize: 'initial', textAlign: 'center', marginTop: '40px'}}>Error : Please check the configuration.</p>
            </div>
        </div>)
    }
};

const App = () => (
    <div>
      <Router>
        <HasAccessToRouter />
      </Router>
    </div>
);

export default App;
