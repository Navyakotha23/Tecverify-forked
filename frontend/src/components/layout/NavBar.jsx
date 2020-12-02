import { useOktaAuth } from '@okta/okta-react';
import React from 'react';
import '../pages/Home.css';
const style = {
    header : {
        color: "white",
        marginLeft: "20px",
        marginTop: "9px",
        width: '100%'
    },
    navBar: {
        background: "#2084ba",
        height: "60px",
        display: "flex"
    }
}
const Navbar = ({mainHeader}) => {
  const { authState, authService } = useOktaAuth();
  const logout = async () => authService.logout('/login');

  return (
    <div>
      <div style={style.navBar}>
          <h1 style={style.header}>{mainHeader}</h1>
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