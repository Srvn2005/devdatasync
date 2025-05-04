import { render, screen } from '@testing-library/react';
import Login from '../components/Login';

test('renders login form', () => {
  render(<Login />);
  expect(screen.getByText(/login/i)).toBeInTheDocument();
});
