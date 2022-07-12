import React, {useEffect} from 'react';
import { BrowserRouter as Router, Route, useHistory } from 'react-router-dom';
import { Security, LoginCallback } from '@okta/okta-react';
import Login from './components/auth/Login';
import { OktaAuth } from '@okta/okta-auth-js'
import Home from './components/pages/Home';
import Dashboard from './components/pages/dashboard';

const HasAccessToRouter = ({config}) => {
    const history = useHistory();
    sessionStorage.setItem('config', JSON.stringify(config));
    let oktaAuth, customAuthHandler;
    const authConfig = {
        clientId: config.CLIENT_ID,
        disableHttpsCheck: true,
        issuer: config.ISSUER,
        pkce: true,
        logo: config.LOGO,
        // redirectUri: `${config.FRONT_END_URL}/implicit/callback`,
        redirectUri: `${config.FRONT_END_URL}/login/callback`,
        authTokenType: config.AUTHORIZE_TOKEN_TYPE,
        scopes: config.SCOPES,
        updateCheckText: config.UPDATE_CHECK_TEXT,
        july12: 'TecVerify 12thJuly 08:10PM'
    };
    sessionStorage.setItem('authConfig', JSON.stringify(authConfig));
    oktaAuth = new OktaAuth(authConfig);
    useEffect(() => {
        customAuthHandler = () => {
            history.push('/login');
        };
    })
    if(typeof authConfig === "object") {
        return (
            <Security
                oktaAuth={oktaAuth}
                onAuthRequired={customAuthHandler}
            >
                <Route path="/" exact component={Dashboard} />
                <Route path="/home" exact component={Home} />
                <Route path="/login/callback" component={LoginCallback} />
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
