import React from 'react';
import { BrowserRouter as Router, Route, useHistory } from 'react-router-dom';
import { Security, SecureRoute, LoginCallback } from '@okta/okta-react';
import Login from './components/auth/Login';
import Navbar from './components/layout/NavBar';
import Home from './components/pages/Home';
import Dashboard from './components/pages/dashboard';

const HasAccessToRouter = () => {
  const history = useHistory();

  const customAuthHandler = () => {
    history.push('/login');
  };
  const config = window.config;
  return (
      <Security
          {...config.authConfig}
          onAuthRequired={customAuthHandler}
      >
        <Navbar mainHeader={config.mainHeader}/>
        <Route path="/" exact component={Dashboard} />
        <SecureRoute path="/home" exact component={Home} />
        <Route path="/implicit/callback" component={LoginCallback} />
        <Route path="/login" exact component={Login} />
      </Security>
  );
};

const App = () => (
    <div>
      <Router>
        <HasAccessToRouter />
      </Router>
    </div>
);

export default App;
