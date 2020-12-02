import React from 'react';
import { BrowserRouter as Router, Route, useHistory } from 'react-router-dom';
import { Security, LoginCallback } from '@okta/okta-react';
import CustomLoginComponent from './components/auth/Login';
import Navbar from './components/layout/NavBar';
import Home from './components/pages/Home';
import Dashboard from './components/pages/dashboard';
import SecureRoute from "@okta/okta-react/dist/SecureRoute";

const HasAccessToRouter = () => {
  const history = useHistory();

  const customAuthHandler = () => {
    history.push('/login');
  };

  return (
    <Security
      {...window.config.authConfig}
      onAuthRequired={customAuthHandler}
    >
      <Navbar />
        <Route path="/" exact component={Dashboard} />
        <SecureRoute path="/home" exact component={Home} />
        <Route path="/implicit/callback" component={LoginCallback} />
        <Route path="/login" exact component={CustomLoginComponent} />
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
