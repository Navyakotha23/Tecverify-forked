import React from 'react';
import { render } from '@testing-library/react';
import Home from './Home';
import { shallow } from 'enzyme';


jest.mock("../auth/Login", () => {
    return <div>SignInWidgetMock</div>;
});

let wrapped = shallow(<Home>title</Home>);
describe('Title', () => {
    it('should render the Title Component correctly', () => {
        expect(wrapped).toMatchSnapshot();
    });
});