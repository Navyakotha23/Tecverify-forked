import React from 'react';
import '../pages/Home.css';

const Footer = () => {
    let backgroundColor = '';
    if(window.config.environment === 'development') {
        backgroundColor = '#ff000078';
    } else if (window.config.environment === 'production'){
        backgroundColor = '#7676762e';
    }
    return (
        <div className={'footer'} style={{backgroundColor: backgroundColor}}>
            <span className={'tenant'}>{window.config.authConfig.issuer.split('/')[2]}</span>
        </div>
    );
};
export default Footer;