import { useOktaAuth } from '@okta/okta-react';
import React from 'react';
import '../pages/Home.css';

const Navbar = ({mainHeader}) => {
  const { authService } = useOktaAuth();
  const logout = async () => authService.logout('/login');

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