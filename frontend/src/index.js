import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

import 'semantic-ui-css/semantic.min.css';

const root = document.getElementById('root');
const url = root.getAttribute('data-url');
const configPromise = fetch(url);
configPromise.then((res) => res.json())
    .then(config => {
        document.title = config.TITLE
        ReactDOM.render(<App config={config}/>, root)
    } );
// ReactDOM.render(<App />, document.getElementById('root'));