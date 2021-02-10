import React from 'react';
import { BrowserRouter as Router, Route, useHistory } from 'react-router-dom';
import { Security, SecureRoute, LoginCallback } from '@okta/okta-react';
import Login from './components/auth/Login';
import { OktaAuth } from '@okta/okta-auth-js'
import Home from './components/pages/Home';
import Dashboard from './components/pages/dashboard';

const HasAccessToRouter = ({config}) => {
    const history = useHistory();
    sessionStorage.setItem('config', JSON.stringify(config));
    const authConfig = {
        clientId: config.CLIENT_ID,
        disableHttpsCheck: config.DISABLE_HTTPS_CHECK,
        issuer: config.ISSUER,
        pkce: config.PKCE,
        redirectUri: `${config.FRONT_END_URL}/implicit/callback`,
        scopes: config.SCOPES
    };
    sessionStorage.setItem('authConfig', JSON.stringify(authConfig));
    const oktaAuth = new OktaAuth(authConfig);
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
                <Route path="/home" exact component={Home} />
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

const App = ({config}) => (
    <div>
      <Router>
        <HasAccessToRouter config={config}/>
      </Router>
    </div>
);

export default App;
