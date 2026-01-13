import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatWithData from './ChatWithData';

// Mock fetch for API calls
describe('ChatWithData Component', () => {
  beforeEach(() => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        body: {
          getReader: () => ({
            read: () => Promise.resolve({ value: new TextEncoder().encode('{"response": "Hello, this is a test response."}\n'), done: false }),
            read: () => Promise.resolve({ value: new TextEncoder().encode('{"response": " I can help with conflict data.", "done": true}\n'), done: true }),
          }),
        },
      })
    );
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('renders chat interface with initial empty state', () => {
    render(<ChatWithData />);
    expect(screen.getByText(/Ask a question about conflict data/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Ask about conflict trends/i)).toBeInTheDocument();
  });

  test('allows user to type and send a message', async () => {
    render(<ChatWithData />);
    const input = screen.getByPlaceholderText(/Ask about conflict trends/i);
    await userEvent.type(input, 'What are the recent conflict trends?');
    expect(input).toHaveValue('What are the recent conflict trends?');
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });
    await waitFor(() => {
      expect(screen.getByText(/What are the recent conflict trends/i)).toBeInTheDocument();
    });
  });

  test('displays AI response with streaming content', async () => {
    render(<ChatWithData />);
    const input = screen.getByPlaceholderText(/Ask about conflict trends/i);
    await userEvent.type(input, 'Tell me about conflicts');
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });
    await waitFor(() => {
      expect(screen.getByText(/Hello, this is a test response/i)).toBeInTheDocument();
    }, { timeout: 2000 });
    await waitFor(() => {
      expect(screen.getByText(/I can help with conflict data/i)).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  test('toggles context sidebar visibility', async () => {
    render(<ChatWithData />);
    const toggleButton = screen.getByTitle(/Collapse Context/i);
    expect(screen.getByText(/AI Context/i)).toBeVisible();
    fireEvent.click(toggleButton);
    expect(screen.getByText(/AI Context/i)).not.toBeVisible();
    fireEvent.click(toggleButton);
    expect(screen.getByText(/AI Context/i)).toBeVisible();
  });

  test('handles API error gracefully', async () => {
    global.fetch = jest.fn(() => Promise.reject(new Error('API down')));
    render(<ChatWithData />);
    const input = screen.getByPlaceholderText(/Ask about conflict trends/i);
    await userEvent.type(input, 'Error test');
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });
    await waitFor(() => {
      expect(screen.getByText(/Error: Unable to fetch response/i)).toBeInTheDocument();
    });
  });
});
