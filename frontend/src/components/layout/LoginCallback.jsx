import React, {useState} from 'react';
import {useOktaAuth} from '@okta/okta-react';
import "../pages/Home.css";

const LoginCallback = () => {

    const { authState, authService } = useOktaAuth();
    console.log(authState.error)
    const [errorMessage, setErrorMessage] = useState('Error : Unable to get Token info.');
    if(authState.error) {
        setErrorMessage(`${authState.error.name} : ${authState.error.message}`);
    } else {
        console.log(errorMessage);
    }
    const logout = async () => authService.logout('/login');
    console.log(authState, authService)
    return (
        !authState.isAuthenticated ? (
            <div className="popup-box">
            <div className="box">
                <p style={{fontSize: "initial"}}>{errorMessage}</p>
                <div style={{width: "100%"}}>
                    <button className="button logout-button" onClick={logout}>
                        logout
                    </button>
                </div>
            </div>
        </div>
        ) : ''
    )
}
export default LoginCallback