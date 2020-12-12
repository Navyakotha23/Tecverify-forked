import React from 'react';
import {useOktaAuth} from '@okta/okta-react';
import "../pages/Home.css";

const LoginError = () => {

    const { authState, authService } = useOktaAuth();
    const logout = async () => authService.logout('/login');
    return (
        !authState.isAuthenticated ? (
            <div className="popup-box" style={{background: '#ffffff50'}}>
            <div className="box">
                <p style={{fontSize: "initial"}}>Error : Unable to get Token info.</p>
                <div style={{width: "100%"}}>
                    <button className="button logout-button" onClick={() => logout()}>
                        logout
                    </button>
                </div>
            </div>
        </div>
        ) : ''
    )
}
export default LoginError