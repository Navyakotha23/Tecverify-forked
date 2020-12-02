import { useOktaAuth } from '@okta/okta-react';
import React from 'react';
import '../pages/Home.css';

const Navbar = () => {
  const { authState, authService } = useOktaAuth();

  const login = async () => authService.login('/login');
  const logout = async () => authService.logout('/login');

  return (
    <div>
      <div style={{background: "#2084ba", height: "70px", display: "flex"}}>
          <h1 style={{color: "white", marginLeft: "20px", marginTop: "14px", width: '100%'}}>TecMFA Bypass Code Generator</h1>
              {
                authState.isAuthenticated ? 
                (
                  <div style={{width: "10%"}}>
                    <button className="button logout-button" onClick={logout}>
                      Logout
                    </button>
                  </div>
                ) : ''
              }
      </div>
    </div>
  );
};
export default Navbar;