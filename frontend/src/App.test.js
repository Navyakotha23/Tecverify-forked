import React from 'react';
import App from './App';
import { shallow } from 'enzyme';

jest.mock("./components/auth/Login", () => {
    return <div>SignInWidgetMock</div>;
});
let wrapped = shallow(<App>title</App>);
describe('Title', () => {
    it('should render the Title Component correctly', () => {
        expect(wrapped).toMatchSnapshot();
    });
});