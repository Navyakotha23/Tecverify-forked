import { useOktaAuth } from '@okta/okta-react';
import React from 'react';
import '../pages/Home.css';

const Navbar = ({mainHeader}) => {
  const { oktaAuth } = useOktaAuth();
  const logout = async () => {
      sessionStorage.removeItem('config');
      sessionStorage.removeItem('authConfig');
      await oktaAuth.signOut('/login');
  };

    return (
      <div className={'navBar'}>
          <div className={'header'}>{mainHeader}</div>
          <button className="logout-button" onClick={logout}>
              Logout
          </button>
      </div>
  );
};
export default Navbar;
