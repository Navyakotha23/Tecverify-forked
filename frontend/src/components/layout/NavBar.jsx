import { useOktaAuth } from '@okta/okta-react';
import React from 'react';
import '../pages/Home.css';

// const Navbar = ({userEmail, mainHeader, closeConnection}) => {
const Navbar = ({userEmail, mainHeader}) => {
    const { oktaAuth } = useOktaAuth();
    const logout = async () => {
        // sessionStorage.removeItem('config');
        // sessionStorage.removeItem('authConfig');
        // await oktaAuth.revokeAccessToken();
        
        // closeConnection();
        await oktaAuth.signOut('/login');
    };

    return (
        <div className={'navBar'}>
            <div className={'header'}>{mainHeader}</div>
            <div>
                <span className="user-email">
                      {userEmail}
                </span>
                <button className="logout-button" onClick={() => logout()}>
                    Logout
                </button>
            </div>
        </div>
    );
};
export default Navbar;
