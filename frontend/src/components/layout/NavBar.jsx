import { useOktaAuth } from '@okta/okta-react';
import React from 'react';
import '../pages/Home.css';
import { useHistory } from "react-router-dom";

const Navbar = ({userEmail, mainHeader}) => {
    const { oktaAuth } = useOktaAuth();
    const history = useHistory();

    const logout = async () => {
        oktaAuth.signOut().then(() =>
            history.push('/login')
        );
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
