import React from 'react';
import { BrowserRouter as Router, Route, useHistory } from 'react-router-dom';
import { Security, SecureRoute, LoginCallback } from '@okta/okta-react';
import Login from './components/auth/Login';
import LoginError from './components/layout/LoginError';
import Home from './components/pages/Home';
import Dashboard from './components/pages/dashboard';

const HasAccessToRouter = () => {
  const history = useHistory();

  const customAuthHandler = () => {
    history.push('/login');
  };
  const config = window.config;
    if(typeof config === "object") {
        return (
            <Security
                {...config.authConfig}
                onAuthRequired={customAuthHandler}
            >
                <LoginError />
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