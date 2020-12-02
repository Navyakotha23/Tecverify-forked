import React from 'react';
import '../pages/Home.css';

const Footer = ({environment, issuer, version}) => {
    let backgroundColor = '';
    if(environment === 'DEV') {
        backgroundColor = '#ff000078';
    } else if (environment === 'PROD'){
        backgroundColor = '#7676762e';
    }
    return (
        <div className={'footer'} style={{backgroundColor: backgroundColor}}>
            <span className={'tenant'}>{issuer.split('/')[2]}</span>
            <span style={{float: 'right', marginRight: '20px'}}>version {version}</span>
        </div>
    );
};
export default Footer;